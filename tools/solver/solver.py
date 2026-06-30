__all__ = "Solver"


from tools.system import System
from tools.preprocessing import registry


class Solver():
    def __init__(self):
        self.METHODS = {
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

    def jacobi_method(self, system: System, **kwargs):
        a, b = self._apply_preprocessing(system, kwargs)
        print(a,b)

    def seidel_method(self, system: System, **kwargs):
        a, b = self._apply_preprocessing(system, kwargs)
        print(a, b)

    def monte_carlo_method(self, system: System, **kwargs):
        pass
