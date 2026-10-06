__all__ = "ExactSolver"

import numpy as np

from typing import Any

from .solver import Solver
from tools.system import System
from tools.solverresultinfo import SolverResultInfo


class InvMatrixSolver(Solver):
    def solve(self, system: System, params: dict[str, Any]) -> SolverResultInfo:

        a = system.get_x()
        b = system.get_y()

        a_inv = np.linalg.inv(a)

        x = a_inv @ b

        resultinfo = SolverResultInfo()
        resultinfo.add_solution(x)

        return resultinfo
