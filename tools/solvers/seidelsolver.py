__all__ = "SeidelSolver"

from typing import Any

import numpy as np

from .solver import Solver
from tools.system import System
from tools.solverresultinfo import SolverResultInfo
from tools.exceptions import MaxIterationsExceeded


class SeidelSolver(Solver):
    def solve(self, system: System, params: dict[str, Any]):
        B, b = self._apply_preprocessing(system, params)

        eps = params.get("eps", 0.01)
        limit = params.get("limit", 15)
        n = system.get_n()
        x = np.copy(b)

        for iteration in range(limit):
            x_old = np.copy(x)

            for i in range(n):
                s = 0.0
                for j in range(n):
                    s += B[i][j] * x[j]

                x[i] = s + b[i]

            error = np.max(np.abs(x - x_old))

            if error < eps:
                return self._build_result_info(
                    x,
                    iteration=iteration + 1,
                    mtrx=B
                )

        raise MaxIterationsExceeded()