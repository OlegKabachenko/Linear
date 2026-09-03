__all__ = "JacobiSolver"

from typing import Any
from multiprocessing import Pool

import numpy as np

from .solver import Solver

from tools.system import System
from tools.solverresultinfo import SolverResultInfo
from tools.parallelexecutionpolicy import ParallelExecutionPolicy
from tools.exceptions import MaxIterationsExceeded


class JacobiSolver(Solver):
    def _compute_row_jacobi(self, B, b, x, i):
        s = 0.0
        for j in range(len(B[i])):
            s += B[i][j] * x[j]

        return s + b[i]

    def _serial_iteration_jacobi(self, B, b, x, x_new):
        n = len(B)

        for i in range(n):
            value = self._compute_row_jacobi(B, b, x, i)
            x_new[i] = value

    def _compute_chunk_jacobi(self, args):
        B, b, x, indices = args
        result = []

        for i in indices:
            value = self._compute_row_jacobi(B, b, x, i)
            result.append((i, value))

        return result

    def _parallel_iteration_jacobi(self, pool, B, b, x, x_new, indices):
        args = [(B, b, x, idx) for idx in indices]

        results = pool.map(self._compute_chunk_jacobi, args)

        for chunk in results:
            for i, value in chunk:
                x_new[i] = value

    def solve(self, system: System, params: dict[str, Any]):
        B, b = self._apply_preprocessing(system, params)

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
                    self._parallel_iteration_jacobi(
                        pool, B, b, x, x_new, indices
                    )
                else:
                    self._serial_iteration_jacobi(
                        B, b, x, x_new
                    )

                error = np.max(np.abs(x_new - x))

                if error < eps:
                    return self._build_result_info(
                        x_new,
                        iteration=iteration + 1,
                        mtrx=B
                    )

                x[:] = x_new

        finally:
            if pool is not None:
                pool.close()
                pool.join()

        raise MaxIterationsExceeded()
