__all__ = "Solver, MaxIterationsExceeded"


from typing import Any
import numpy as np

from tools.system import System
from tools.preprocessing import registry


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

    def jacobi_method(self, system: System, params: dict[str, Any]):
        a, b = self._apply_preprocessing(system, params)

        eps = params.get("eps", 0.01)
        limit = params.get("limit", 15)

        n = system.get_n()
        x = np.copy(b)
        x_new = np.copy(x)

        for iteration in range(limit):
            for i in range(n):
                s = 0.0
                for j in range(n):
                    s += a[i][j] * x[j]

                x_new[i] = s + b[i]

            error = np.max(np.abs(x_new - x))

            if error < eps:
                return x_new, iteration + 1, error

            x = np.copy(x_new)

        raise MaxIterationsExceeded()

    def seidel_method(self, system: System, params: dict[str, Any]):
        a, b = self._apply_preprocessing(system, kwargs)


    def monte_carlo_method(self, system: System, params: dict[str, Any]):
        pass
