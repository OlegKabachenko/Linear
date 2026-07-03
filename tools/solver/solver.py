__all__ = "Solver, MaxIterationsExceeded"


from typing import Any
import numpy as np
from multiprocessing import Pool


from tools.system import System
from tools.preprocessing import registry
from tools.parallelexecutionpolicy import ParallelExecutionPolicy


class MaxIterationsExceeded(Exception):
    pass


class Solver():
    def __init__(self):
        self.METHODS: dict[str, dict[str, object]] = {
            "Метод Якобі": {
                "function": self.jacobi_method,
                "extra_widget": "classic_methods_param",
                "can_be_parallel": True
            },
            "Метод Зейделя": {
                "function": self.seidel_method,
                "extra_widget": "classic_methods_param",
                "can_be_parallel": False
            },
            "Метод Монте-Карло": {
                "function": self.monte_carlo_method,
                "extra_widget": "monte_param",
                "can_be_parallel": True
            }
        }

    def _apply_preprocessing(self, system: System, params):
        strategy = registry.get_by_key(params["p_type"])

        a = system.get_x()
        b = system.get_y()

        return strategy.process(a, b, params)

    def _compute_row_jacobi(self, a, b, x, i):
        s = 0.0
        for j in range(len(a[i])):
            s += a[i][j] * x[j]

        return s + b[i]

    def _serial_iteration_jacobi(self, a, b, x, x_new):
        n = len(a)

        for i in range(n):
            value = self._compute_row_jacobi(a, b, x, i)
            x_new[i] = value

    def _compute_chunk_jacobi(self, args):
        a, b, x, indices = args
        result = []

        for i in indices:
            value = self._compute_row_jacobi(a, b, x, i)
            result.append((i, value))

        return result

    def _parallel_iteration_jacobi(self, pool, a, b, x, x_new, indices):
        args = [(a, b, x, idx) for idx in indices]

        results = pool.map(self._compute_chunk_jacobi, args)

        for chunk in results:
            for i, value in chunk:
                x_new[i] = value

    def jacobi_method(self, system: System, params: dict[str, Any], parallel: bool = False):
        a, b = self._apply_preprocessing(system, params)

        eps = params.get("eps", 0.01)
        limit = params.get("limit", 15)

        n = system.get_n()
        x = np.copy(b)
        x_new = np.copy(x)

        pool = None
        indices = None

        if parallel:
            processes = ParallelExecutionPolicy.get_process_count(n)
            indices = np.array_split(range(n), processes)
            pool = Pool(processes=processes)

        try:
            for iteration in range(limit):
                if parallel:
                    self._parallel_iteration_jacobi(pool, a, b, x, x_new, indices)
                else:
                    self._serial_iteration_jacobi(a, b, x, x_new)

                error = np.max(np.abs(x_new - x))

                if error < eps:
                    return x_new, iteration + 1

                x[:] = x_new
        finally:
            if pool is not None:
                pool.close()
                pool.join()

        raise MaxIterationsExceeded()

    def seidel_method(self, system: System, params: dict[str, Any], parallel: bool = False):
        a, b = self._apply_preprocessing(system, params)

        eps = params.get("eps", 0.01)
        limit = params.get("limit", 15)
        n = system.get_n()
        x = np.copy(b)

        for iteration in range(limit):
            x_old = np.copy(x)

            for i in range(n):
                s = 0.0
                for j in range(n):
                    s += a[i][j] * x[j]

                x[i] = s + b[i]

            error = np.max(np.abs(x - x_old))

            if error < eps:
                return x, iteration + 1

        raise MaxIterationsExceeded()

    def monte_carlo_method(self, system: System, params: dict[str, Any], parallel: bool = False):
        pass
