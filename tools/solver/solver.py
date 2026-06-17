__all__ = "Solver"


class Solver():
    def __init__(self):
        self.METHODS = {
            "Метод Якобі": {
                "function": self.jacobi_method,
                "extra_widget": "classic_methods_param"
            },
            "Метод Зейделя": {
                "function": self.seidel_method,
                "extra_widget": "classic_methods_param"
            },
            "Метод Монте-Карло": {
                "function": self.monte_carlo_method,
                "extra_widget": "monte_param"
            }
        }

    def jacobi_method(self):
        pass

    def seidel_method(self):
        pass

    def monte_carlo_method(self):
        pass
