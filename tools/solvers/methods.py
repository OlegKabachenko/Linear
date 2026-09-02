__all__ = "METHODS"

from typing import TypedDict

from .solver import Solver
from .exactsolver import ExactSolver
from .jacobisolver import JacobiSolver
from .seidelsolver import SeidelSolver
from .montecarlosolver import MonteCarloSolver


class MethodInfo(TypedDict):
    solver: type[Solver]
    extra_widget: str | None
    can_be_parallel: bool


METHODS: dict[str, MethodInfo] = {
    "Точний метод": {
        "solver": ExactSolver,
        "extra_widget": None,
        "can_be_parallel": False,
    },

    "Метод Якобі": {
        "solver": JacobiSolver,
        "extra_widget": "classic_methods_param",
        "can_be_parallel": True,
    },

    "Метод Зейделя": {
        "solver": SeidelSolver,
        "extra_widget": "classic_methods_param",
        "can_be_parallel": False,
    },

    "Метод Монте-Карло": {
        "solver": MonteCarloSolver,
        "extra_widget": "monte_param",
        "can_be_parallel": True,
    },
}