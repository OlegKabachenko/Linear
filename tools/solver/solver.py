__all__ = "Solver"


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

    def jacobi_method(self):
        pass

    def seidel_method(self):
        pass

    def monte_carlo_method(self):
        pass
