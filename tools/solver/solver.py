__all__ = "Solver, MaxIterationsExceeded"

import numpy as np
import time

from typing import Any
from multiprocessing import Pool

from scipy.stats import t

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

    def get_norms(self, mtrx):
        m = np.max(np.sum(np.abs(mtrx), axis=1))
        n = np.max(np.sum(np.abs(mtrx), axis=0))

        return m, n

    def get_spectral_radius(self, mtrx):
        eigenvalues = np.linalg.eigvals(mtrx)
        spectral_radius = max(abs(eigenvalues))
        return spectral_radius

    def _build_result_info(self, x, iteration=None, mtrx=None):
        resultinfo = SolverResultInfo()

        resultinfo.add_solution(x)

        if iteration is not None:
            resultinfo.add_iterations(iteration)

        if mtrx is not None:
            resultinfo.add_spectral_radius(
                self.get_spectral_radius(mtrx)
            )

            m, n = self.get_norms(mtrx)
            resultinfo.add_norms(m, n)

        return resultinfo

    def exact_method(self, system, params: dict[str, Any]):
        a = system.get_x()
        b = system.get_y()

        x = np.linalg.inv(a) @ b

        return self._build_result_info(x)

    def jacobi_method(self, system: System, params: dict[str, Any]):
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
                    self._parallel_iteration_jacobi(pool, B, b, x, x_new, indices)
                else:
                    self._serial_iteration_jacobi(B, b, x, x_new)

                error = np.max(np.abs(x_new - x))

                if error < eps:
                    return self._build_result_info(
                        x_new,
                        iteration=iteration+1,
                        mtrx=B
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

    def monte_worker(self, B, b, prob, n, k):
        rng = Generator(Philox())

        x_cnt = len(b)
        results = [[] for _ in range(x_cnt)]

        for start_state in range(x_cnt):
            for _ in range(n):
                curr_state = start_state
                value = b[curr_state]
                w = 1.0

                for _ in range(k):
                    next_state = rng.choice(x_cnt, p=prob[curr_state])

                    transition_weight = (B[curr_state, next_state] / prob[curr_state, next_state])

                    w *= transition_weight
                    curr_state = next_state

                    value += w * b[curr_state]

                results[start_state].append(value)

        return results

    def choose_trj_lnght(self, B, b, eps):
        q = np.linalg.norm(B, ord=np.inf)
        b_norm = np.linalg.norm(b, ord=np.inf)

        if b_norm == 0 or q == 0:
            return 0

        val = eps *(1-q)/b_norm
        k = int(np.ceil(np.log(val)/np.log(q) - 1))
        return k

    def monte_carlo_method(self, system: System, params: dict[str, Any]):
        B, b = self._apply_preprocessing(system, params)

        eps = params.get("eps", 0.1)
        alpha = params.get("alpha", 0.05)

        eps_k = eps * 0.4
        eps_mc = eps * 0.6

        start_n = params.get("start_monte_n", 20)
        max_n = params.get("max_monte_n", 1000000)

        parallel = params.get("is_parallel", False)

        if start_n > max_n:
            raise MaxIterationsExceeded()

        k = self.choose_trj_lnght(B, b, eps_k)

        row_sums = np.sum(np.abs(B), axis=1)
        prob = np.abs(B) / row_sums[:, None]

        x_cnt = len(b)

        results = [[] for _ in range(x_cnt)]

        current_n = 0
        n_total = start_n

        while True:
            # Number of new trajectories that must be generated
            n_to_generate = n_total - current_n

            if not parallel:
                new_results = self.monte_worker(B, b, prob, n_to_generate,k)

                for i in range(x_cnt):
                    results[i].extend(new_results[i])

            else:
                processes = ParallelExecutionPolicy.get_process_count(n_to_generate)

                base_n = n_to_generate // processes
                remainder = n_to_generate % processes

                n_per_process = [
                    base_n + (1 if i < remainder else 0)
                    for i in range(processes)
                ]

                with Pool(processes=processes) as pool:
                    process_results = pool.starmap(
                        self.monte_worker,
                        [
                            (B, b, prob, n_local, k)
                            for n_local in n_per_process
                            if n_local > 0
                        ]
                    )

                for process_result in process_results:
                    for i in range(x_cnt):
                        results[i].extend(process_result[i])

            current_n = n_total

            results_array = np.asarray(results)

            t_value = t.ppf(1 - alpha / 2, df=n_total - 1)

            x = np.mean(results_array, axis=1)
            s = np.std(results_array, axis=1, ddof=1)

            deltas = t_value * s / np.sqrt(n_total)

            max_delta = np.max(deltas)
            max_i = np.argmax(deltas)

            if max_delta <= eps_mc:
                break

            n_new = int(np.ceil((t_value * s[max_i] / eps_mc) ** 2))

            if n_new > max_n:
                raise MaxIterationsExceeded()

            if n_total > n_new:  #Theoretically, this exeption should not appear, if code is ok
                raise Exception(
                    "n_total > n_new, check programm logic!"
                )

            n_total = n_new

        resultinfo = self._build_result_info(
            x,
            iteration=n_total,
            mtrx=B
        )

        resultinfo.add(
            "k",
            k,
            "Довжина ланцюга",
            bold=True,
            value_format="int",
            order=100
        )

        return resultinfo

