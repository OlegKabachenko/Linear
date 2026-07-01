import numpy as np


class PreprocessingStrategy:
    key = None
    label = None

    def process(self, a, b, params):
        raise NotImplementedError


class Preconditioning(PreprocessingStrategy):
    key = "prec"
    label = "Попереднє кондиціонування"

    def custom_round(self, a):
        sign = np.sign(a)

        abs_a = np.abs(a)
        a_round_abs = np.where(abs_a % 1 >= 0.7, np.ceil(abs_a), np.floor(abs_a))

        return a_round_abs * sign

    def scale_matrix(self, a, scale=10):
        a_scaled = a * scale
        return self.custom_round(a_scaled)

    def is_diagonally_dominant(self, a):
        n = len(a)
        for i in range(n):
            diag = abs(a[i][i])
            off_diag_sum = np.sum(np.abs(a[i])) - diag
            if diag < off_diag_sum:
                return False
        return True

    def to_dominant(self, a, b):
        n = len(a)

        new_a = np.zeros_like(a)
        new_b = np.zeros_like(b)

        row_sums = np.sum(np.abs(a), axis=1)
        used = set()

        for i in range(n):
            values = np.zeros(n)

            for j in range(n):
                if j in used:
                    values[j] = -np.inf
                else:
                    diag_val = np.abs(a[j, i])
                    values[j] = diag_val - (row_sums[j] - diag_val)

            max_index = np.argmax(values)

            new_a[i] = a[max_index]
            new_b[i] = b[max_index]
            used.add(max_index)
        return new_a, new_b

    def to_canonical_iterative_form(self, a, b):
        n = len(a)

        c = np.zeros((n, n))
        d = np.zeros(n)

        for i in range(n):
            diag = a[i][i]

            for j in range(n):
                if i == j:
                    c[i][j] = 0.0
                else:
                    c[i][j] = -a[i][j] / diag

            d[i] = b[i] / diag

        return c, d

    def process(self, a, b, params):
        scale = params["scale"]
        a_inv = np.linalg.inv(a)
        c = self.scale_matrix(a_inv, scale)

        an = c @ a
        bn = c @ b

        if not (self.is_diagonally_dominant(an)):
            an, bn = self.to_dominant(an, bn)

        an, bn = self.to_canonical_iterative_form(an, bn)

        return an, bn


class Spectral(PreprocessingStrategy):
    key = "spectral"
    label = "Спектральний критерій"

    def process(self, a, b, params):
        eigenvalues = np.linalg.eigvals(a)

        spectral_radius = max(abs(eigenvalues))
        a_inv = np.linalg.inv(a)

        v = 1 / spectral_radius

        eps = v / 10

        alpha = a * eps

        i = np.eye(a.shape[0])
        beta = (a_inv - eps * i) @ b

        return alpha, beta


class NonePreprocessing(PreprocessingStrategy):
    key = "none"
    label = "Без передобробки"

    def process(self, a, b, params):
        return a, b


class PreprocessingRegistry:
    def __init__(self):
        self._by_id = {}
        self._by_key = {}

    def register(self, idx, strategy):
        self._by_id[idx] = strategy
        self._by_key[strategy.key] = strategy

    def get_by_id(self, idx):
        return self._by_id[idx]

    def get_by_key(self, key):
        return self._by_key[key]

    def items(self):
        return [(i, s.label) for i, s in self._by_id.items()]


registry = PreprocessingRegistry()

registry.register(0, Preconditioning())
registry.register(1, Spectral())
registry.register(2, NonePreprocessing())