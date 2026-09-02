
__all__ = ["Solver", "MaxIterationsExceeded"]

import numpy as np

from abc import ABC, abstractmethod
from typing import Any

from tools.system import System
from tools.solverresultinfo import SolverResultInfo
from tools.preprocessing import registry

from typing import TypedDict, Callable, Any


class Solver(ABC):
    def _apply_preprocessing(self, system, params):
        strategy = registry.get_by_key(params["p_type"])

        a = system.get_x()
        b = system.get_y()

        return strategy.process(a, b, params)

    def get_norms(self, mtrx):
        m = np.max(np.sum(np.abs(mtrx), axis=1))
        n = np.max(np.sum(np.abs(mtrx), axis=0))

        return m, n

    def get_spectral_radius(self, mtrx):
        eigenvalues = np.linalg.eigvals(mtrx)
        return max(abs(eigenvalues))

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

    @abstractmethod
    def solve(self, system: System, params: dict[str, Any]) -> SolverResultInfo:
        pass
