__all__ = "ExactSolver"

import numpy as np

from typing import Any

from .solver import Solver
from tools.system import System
from tools.solverresultinfo import SolverResultInfo


class ExactSolver(Solver):
    def solve(self, system: System, params: dict[str, Any]) -> SolverResultInfo:

        a = system.get_x()
        b = system.get_y()

        x = np.linalg.solve(a, b)

        resultinfo = SolverResultInfo()
        resultinfo.add_solution(x)

        return resultinfo
