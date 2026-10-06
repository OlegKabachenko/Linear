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
from tools.exceptions import NotTridiagonalError


class MonteCarloSolver(Solver):
    def _find_alpha(self, B, d, I, step=0.1, max_val=1.5, min_val=-1.5):
        tol = 1e-2
        for alpha in np.arange(max_val, min_val - step, -step):
            b_mod = (1 - alpha) * I + alpha * B
            b_mod_norms = self.get_norms(b_mod)
            b_mod_abs_rad = self.get_spectral_radius(np.abs(b_mod))

            if min(b_mod_norms) < 1 - tol or b_mod_abs_rad < 1 - tol:
                d_mod = alpha * d
                return b_mod, d_mod

        return None

    def _prepare_for_chain_length(self, B, d):
        I = np.eye(len(d))

        result = self._find_alpha(B, d, I)
        if result is not None:
            return result

        b_new = I - np.transpose(I - B) @ (I - B)
        d_new = np.transpose(I - B) @ d

        norms = self.get_norms(b_new)
        s_rad = self.get_spectral_radius(b_new)
        s_rad_abs = self.get_spectral_radius(np.abs(b_new))

        if min(norms) < 1 or (s_rad < 1 and s_rad_abs<1):
            return b_new, d_new

        result = self._find_alpha(b_new, d_new, I)
        if result is not None:
            return result
        else:
            raise ValueError("k error")

    def choose_trj_lnght(self, B, d, eps):
        d_norm = np.linalg.norm(d, ord=np.inf)
        norm = np.linalg.norm(B, ord=np.inf)

        if norm >= 1:
            norm = np.linalg.norm(B, ord=1)
            d_norm = np.linalg.norm(d, ord=1)

        if d_norm == 0 or norm == 0:
            return 0, B, d

        if norm >= 1:
            ro_module_b = self.get_spectral_radius(np.abs(B))

            if ro_module_b >= 1:
                B_new, d_new = self._prepare_for_chain_length(B, d)
                return self.choose_trj_lnght(B_new, d_new, eps)
            else:
                return None, B, d

        val = eps * (1 - norm) / d_norm
        k = int(np.ceil(np.log(val) / np.log(norm) - 1))

        return k, B, d

    def _get_next_state(self, curr_state, rng, B, prob):
        next_state = rng.choice(len(B), p=prob[curr_state])

        transition_value = B[curr_state, next_state]
        transition_prob = prob[curr_state, next_state]

        return next_state, transition_value, transition_prob

    def _get_tridiagonal_next_state(self, curr_state, rng, lower, diag, upper, prob_lower, prob_diag, prob_upper):
        probabilities = (
            prob_lower[curr_state],
            prob_diag[curr_state],
            prob_upper[curr_state]
        )

        direction = rng.choice(3, p=probabilities)

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

        return next_state, transition_value, transition_prob

    def monte_worker(self, d, n, k, data, tridiagonal=False, eps_k=None, max_steps=900):
        rng = Generator(Philox())
        x_cnt = len(d)
        results = [[] for _ in range(x_cnt)]

        if tridiagonal:
            B, lower, diag, upper, prob_lower, prob_diag, prob_upper = data

        else:
            B, prob = data

        #only for dynamic stopping
        if k is None:
            if self.get_spectral_radius(np.abs(B)) >= 1:
                raise Exception()

            h = np.linalg.inv(np.eye(x_cnt) - np.abs(B)) @ np.abs(d)

        for start_state in range(x_cnt):
            for i in range(n):
                curr_state = start_state
                value = d[curr_state]
                w = 1.0

                step = 0
                while True:
                    # Fixed-length mode
                    if k is not None and step >= k:
                        break

                    # Dynamic stopping mode
                    if k is None:
                        if abs(w)*h[curr_state] < eps_k:
                            break

                    # Safety limit
                    if step >= max_steps:
                        raise MaxIterationsExceeded()

                    if tridiagonal:
                        next_state, transition_value, transition_prob = self._get_tridiagonal_next_state(curr_state, rng, lower, diag, upper, prob_lower, prob_diag, prob_upper)
                    else:
                        next_state, transition_value, transition_prob = self._get_next_state(curr_state, rng, B, prob)

                    transition_weight = (transition_value / transition_prob)

                    w *= transition_weight
                    curr_state = next_state

                    value += w * d[curr_state]
                    step += 1

                results[start_state].append(value)
        return results

    def _validate_tridiagonal(self, mtrx):
        n = mtrx.shape[0]

        for i in range(n):
            for j in range(n):
                if abs(i - j) > 1 and mtrx[i, j] != 0:
                    raise NotTridiagonalError()

    def _build_tridiagonal_data(self, B):
        self._validate_tridiagonal(B)

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
            B,
            lower,
            diag,
            upper,
            prob_lower,
            prob_diag,
            prob_upper
        )

    def _prepare_monte_params(self, params, B, d):
        eps = params.get("eps", 0.1)
        alpha = params.get("alpha", 0.05)
        eps_k = eps * 0.2
        eps_mc = eps * 0.8

        start_n = params.get("start_monte_n", 20)
        max_n = params.get("max_monte_n", 1000000)

        parallel = params.get("is_parallel", False)
        tridiagonal = params.get("is_tridiagonal", False)

        if start_n > max_n:
            raise MaxIterationsExceeded()

        k, B, d = self.choose_trj_lnght(B, d, eps_k)

        return (
            alpha,
            eps_mc,
            start_n,
            max_n,
            parallel,
            tridiagonal,
            k,
            eps_k,
            B,
            d
        )

    def _prepare_monte_data(self, tridiagonal, B):
        if tridiagonal:
            return self._build_tridiagonal_data(B)

        else:
            row_sums = np.sum(np.abs(B), axis=1)
            prob = np.abs(B) / row_sums[:, None]
            return B, prob

    def _execute_monte_parallel(self, n, d, k, data, tridiagonal, eps_k):
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
                    (d, n_local, k, data, tridiagonal, eps_k)
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
        B, d = self._apply_preprocessing(system, params)

        (
            alpha,
            eps_mc,
            start_n,
            max_n,
            parallel,
            tridiagonal,
            k,
            eps_k,
            B,
            d
        ) = self._prepare_monte_params(params, B, d)

        x_cnt = len(d)

        data = self._prepare_monte_data(tridiagonal, B)

        results = [[] for _ in range(x_cnt)]

        current_n = 0
        n_total = start_n

        while True:
            n_to_generate = n_total - current_n

            if not parallel:
                new_results = self.monte_worker(d, n_to_generate, k, data, tridiagonal, eps_k)

                for i in range(x_cnt):
                    results[i].extend(new_results[i])

            else:
                process_results = self._execute_monte_parallel(n_to_generate, d, k, data, tridiagonal, eps_k)

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

        if k is None:
            k = "динамічна"

        return self._build_monte_result(x, n_total, B, k)
