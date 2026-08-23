__all__ = "Solver, MaxIterationsExceeded"

import numpy as np
import time

from typing import Any
from multiprocessing import Pool

from tools.system import System
from tools.preprocessing import registry
from tools.parallelexecutionpolicy import ParallelExecutionPolicy
from tools.solverresultinfo import SolverResultInfo

from numpy.random import Generator, Philox

class MaxIterationsExceeded(Exception):
    pass


class Solver():
    def __init__(self):
        self.METHODS: dict[str, dict[str, object]] = {
            "Точний метод": {
                "function": self.exact_method,
                "extra_widget": None,
                "can_be_parallel": False
            },

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

    def get_norms(self, a):
        m = np.max(np.sum(np.abs(a), axis=1))
        n = np.max(np.sum(np.abs(a), axis=0))

        return m, n

    def get_spectral_radius(self, a):
        eigenvalues = np.linalg.eigvals(a)
        spectral_radius = max(abs(eigenvalues))
        return spectral_radius

    def _build_result_info(self, x, iteration=None, a=None):
        resultinfo = SolverResultInfo()

        resultinfo.add_solution(x)

        if iteration is not None:
            resultinfo.add_iterations(iteration)

        if a is not None:
            resultinfo.add_spectral_radius(
                self.get_spectral_radius(a)
            )

            m, n = self.get_norms(a)
            resultinfo.add_norms(m, n)

        return resultinfo

    def exact_method(self, system, params: dict[str, Any]):
        a = system.get_x()
        b = system.get_y()

        x = np.linalg.inv(a) @ b

        return self._build_result_info(x)

    def jacobi_method(self, system: System, params: dict[str, Any]):
        a, b = self._apply_preprocessing(system, params)

        eps = params.get("eps", 0.01)
        limit = params.get("limit", 15)
        parallel = params.get("is_parallel", False)

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
                    return self._build_result_info(
                        x_new,
                        iteration=iteration+1,
                        a=a
                    )

                x[:] = x_new
        finally:
            if pool is not None:
                pool.close()
                pool.join()

        raise MaxIterationsExceeded()

    def seidel_method(self, system: System, params: dict[str, Any]):
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
                return self._build_result_info(
                    x,
                    iteration=iteration + 1,
                    a=a
                )

        raise MaxIterationsExceeded()

    def monte_worker(self, a, b, n, k):
        row_sums = np.sum(np.abs(a), axis=1)
        prob = np.abs(a) / row_sums[:, None]

        rng = Generator(Philox())

        x_cnt = len(b)
        x = np.zeros(x_cnt)

        for start_state in range(x_cnt):
            results = []

            for walk in range(n):
                curr_state = start_state


                value = b[curr_state]
                w = 1.0

                for _ in range(k):
                    next_state = rng.choice(x_cnt, p=prob[curr_state])

                    transition_weight = (a[curr_state, next_state] / prob[curr_state, next_state])

                    w *= transition_weight
                    curr_state = next_state

                    value += w * b[curr_state]

                results.append(value)

            x[start_state] = np.mean(results)

        return x

    def monte_carlo_method(self, system: System, params: dict[str, Any]):
        a, b = self._apply_preprocessing(system, params)

        parallel = params.get("is_parallel", False)
        n = params.get("n", 10000)
        k = params.get("trajectory_lenght", 20)

        if not parallel:
            x = self.monte_worker(a, b, n, k)

        else:
            processes = ParallelExecutionPolicy.get_process_count(n)

            base_n = n // processes
            remainder = n % processes

            n_per_process = [
                base_n + (1 if i < remainder else 0)
                for i in range(processes)
            ]

            with Pool(processes=processes) as pool:
                results = pool.starmap(
                    self.monte_worker,
                    [
                        (a, b, n_local, k)
                        for n_local in n_per_process
                    ]
                )

            x = np.mean(results, axis=0)

        return self._build_result_info(
            x,
            a=a
        )




