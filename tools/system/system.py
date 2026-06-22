import numpy as np

class System:
    def __init__(self, n, x, y):
        self.__n = None
        self.__x = None
        self.__y = None

        self.set_params(n, x, y)

    def set_params(self, n, x, y):
        if n is None:
            return

        n_validated = self.__validate_n(n)
        x_validated = self.__validate_x(x, n_validated)
        y_validated = self.__validate_y(y, n_validated)

        self.__n = n_validated
        self.__x = x_validated
        self.__y = y_validated

    def get_x(self):
        return np.asarray(self.__x, dtype=float)

    def get_y(self):
        return np.asarray(self.__y, dtype=float)

    def get_n(self):
        return self.__n

    def __validate_n(self, n):
        if not isinstance(n, int):
            raise ValueError("Invalid type for n")
        if n <= 1:
            raise ValueError("n must be > 1")
        return n

    def __validate_x(self, x, n):
        x = np.asarray(x, dtype=float)

        if x.shape != (n, n):
            raise ValueError(f"x must have shape ({n}, {n}), got {x.shape}")

        return x

    def __validate_y(self, y, n):
        y = np.asarray(y, dtype=float)

        if y.shape != (n,):
            raise ValueError(f"y must have shape ({n},) got {y.shape}")

        return y

