class System:
    def __init__(self, n, x, y):
        self.__n = None
        self.__x = None
        self.__y = None

        self.set_params(n, x, y)

    def set_params(self, n, x, y):
        if n is None:
            return

        n_validated = self.__validate_field("n", n, expected_type=int)
        x_validated = self.__validate_field("x", x, expected_type=list, length=n * n)
        y_validated = self.__validate_field("y", y, expected_type=list, length=n)

        self.__n = n_validated
        self.__x = x_validated
        self.__y = y_validated

    def set_x (self, x):
        lenght = self.__n * self.__n
        x_validated = self.__validate_field("x", x, expected_type=list, length=lenght)
        self.__x = x_validated

    def set_y (self, y):
        lenght = self.__n
        y_validated = self.__validate_field("y", y, expected_type=list, length=lenght)
        self.__y = y_validated

    def get_n(self):
        return self.__n

    def get_x(self):
        return self.__x

    def get_y(self):
        return self.__y

    def __validate_field(self, name, value, *, expected_type=None, length=None):

        if expected_type and not isinstance(value, expected_type):
            raise ValueError(f"Invalid type for {name}")

        if length is not None:
            if len(value) != length:
                raise ValueError(f"Invalid length for {name}")
        return value