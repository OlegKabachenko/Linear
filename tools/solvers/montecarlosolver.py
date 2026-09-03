__all__ = "MonteCarloSolver"

from multiprocessing import Pool

import numpy as np
from numpy.random import Generator, Philox
from scipy.stats import t

from typing import Any

from .solver import Solver
from tools.system import System
from tools.parallelexecutionpolicy import ParallelExecutionPolicy
from tools.solverresultinfo import SolverResultInfo
from tools.exceptions import MaxIterationsExceeded


class MonteCarloSolver(Solver):
    def choose_trj_lnght(self, B, b, eps):
        q = np.linalg.norm(B, ord=np.inf)
        b_norm = np.linalg.norm(b, ord=np.inf)

        if b_norm == 0 or q == 0:
            return 0

        val = eps * (1-q)/b_norm
        k = int(np.ceil(np.log(val)/np.log(q) - 1))
        return k

    def monte_worker(self, b, n, k, data, tridiagonal=False):
        rng = Generator(Philox())

        x_cnt = len(b)
        results = [[] for _ in range(x_cnt)]

        if tridiagonal:
            (
                lower,
                diag,
                upper,
                prob_lower,
                prob_diag,
                prob_upper
            ) = data

        else:
            B, prob = data

        for start_state in range(x_cnt):
            for _ in range(n):
                curr_state = start_state
                value = b[curr_state]
                w = 1.0

                for _ in range(k):
                    if tridiagonal:
                        probabilities = (
                            prob_lower[curr_state],
                            prob_diag[curr_state],
                            prob_upper[curr_state]
                        )

                        direction = rng.choice(
                            3,
                            p=probabilities
                        )

                        if direction == 0:
                            next_state = curr_state - 1
                            transition_value = lower[curr_state]
                            transition_prob = prob_lower[curr_state]

                        elif direction == 1:
                            next_state = curr_state
                            transition_value = diag[curr_state]
                            transition_prob = prob_diag[curr_state]

                        else:
                            next_state = curr_state + 1
                            transition_value = upper[curr_state]
                            transition_prob = prob_upper[curr_state]

                    else:
                        next_state = rng.choice(x_cnt, p=prob[curr_state])
                        transition_value = B[curr_state, next_state]
                        transition_prob = prob[curr_state, next_state]

                    transition_weight = (transition_value / transition_prob)

                    w *= transition_weight
                    curr_state = next_state

                    value += w * b[curr_state]

                results[start_state].append(value)

        return results

    def _build_tridiagonal_data(self, B):
        n = B.shape[0]

        lower = np.zeros(n)
        diag = np.diag(B).copy()
        upper = np.zeros(n)

        for i in range(n):
            if i > 0:
                lower[i] = B[i, i - 1]

            if i < n - 1:
                upper[i] = B[i, i + 1]

        row_sums = (
                np.abs(lower)
                + np.abs(diag)
                + np.abs(upper)
        )

        prob_lower = np.abs(lower) / row_sums
        prob_diag = np.abs(diag) / row_sums
        prob_upper = np.abs(upper) / row_sums

        return (
            lower,
            diag,
            upper,
            prob_lower,
            prob_diag,
            prob_upper
        )

    def _prepare_monte_params(self, params, B, b):
        eps = params.get("eps", 0.1)
        alpha = params.get("alpha", 0.05)
        eps_k = eps * 0.4
        eps_mc = eps * 0.6

        start_n = params.get("start_monte_n", 20)
        max_n = params.get("max_monte_n", 1000000)

        parallel = params.get("is_parallel", False)
        tridiagonal = params.get("is_tridiagonal", False)

        if start_n > max_n:
            raise MaxIterationsExceeded()

        k = self.choose_trj_lnght(B, b, eps_k)

        return (
            alpha,
            eps_mc,
            start_n,
            max_n,
            parallel,
            tridiagonal,
            k
        )

    def _prepare_monte_data(self, tridiagonal, B):
        if tridiagonal:
            return self._build_tridiagonal_data(B)

        else:
            row_sums = np.sum(np.abs(B), axis=1)
            prob = np.abs(B) / row_sums[:, None]
            return B, prob

    def _execute_monte_parallel(self, n, b, k, data, tridiagonal):
        processes = ParallelExecutionPolicy.get_process_count(n)

        base_n = n // processes
        remainder = n % processes

        n_per_process = [
            base_n + (1 if i < remainder else 0)
            for i in range(processes)
        ]

        with Pool(processes=processes) as pool:
            process_results = pool.starmap(
                self.monte_worker,
                [
                    (b, n_local, k, data, tridiagonal)
                    for n_local in n_per_process
                    if n_local > 0
                ]
            )
        return process_results

    def _check_monte_precision(self, results, n_total, alpha, eps_mc):
        results_array = np.asarray(results)

        t_value = t.ppf(1 - alpha / 2, df=n_total - 1)

        x = np.mean(results_array, axis=1)
        s = np.std(results_array, axis=1, ddof=1)

        deltas = t_value * s / np.sqrt(n_total)

        max_delta = np.max(deltas)
        max_i = np.argmax(deltas)

        if max_delta <= eps_mc:
            return x, None

        n_new = int(np.ceil((t_value * s[max_i] / eps_mc) ** 2))

        return x, n_new

    def _build_monte_result(self, x, n_total, B, k):
        resultinfo = self._build_result_info(x, iteration=n_total, mtrx=B)

        resultinfo.add(
            "k",
            k,
            "Довжина ланцюга",
            bold=True,
            value_format="int",
            order=100
        )
        return resultinfo

    def solve(self, system: System, params: dict[str, Any]):
        B, b = self._apply_preprocessing(system, params)

        (
            alpha,
            eps_mc,
            start_n,
            max_n,
            parallel,
            tridiagonal,
            k
        ) = self._prepare_monte_params(params, B, b)

        x_cnt = len(b)

        data = self._prepare_monte_data(tridiagonal, B)

        results = [[] for _ in range(x_cnt)]

        current_n = 0
        n_total = start_n

        while True:
            # Number of new trajectories that must be generated
            n_to_generate = n_total - current_n

            if not parallel:
                new_results = self.monte_worker(b, n_to_generate, k, data, tridiagonal)

                for i in range(x_cnt):
                    results[i].extend(new_results[i])

            else:
                process_results = self._execute_monte_parallel(n_to_generate, b, k, data, tridiagonal)

                for process_result in process_results:
                    for i in range(x_cnt):
                        results[i].extend(process_result[i])

            current_n = n_total

            x, n_new = self._check_monte_precision(results, n_total, alpha, eps_mc)

            if n_new is None:
                break

            if n_new > max_n:
                raise MaxIterationsExceeded()

            if n_new < n_total:
                raise Exception("n_total > n_new, check program logic!")

            n_total = n_new

        return self._build_monte_result(x, n_total, B, k)
