import numpy as np
from scipy.optimize import linear_sum_assignment


class FailedPreprocessingStrategy(Exception):
    pass


class PreprocessingStrategy:
    key = None
    label = None

    def process(self, a, b, params):
        raise NotImplementedError

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

        row_sums = np.sum(np.abs(a), axis=1)
        score = np.empty((n, n))

        for row in range(n):
            for col in range(n):

                diag = abs(a[row, col])

                if diag == 0:
                    score[row, col] = -1e9
                else:
                    off = row_sums[row] - diag
                    score[row, col] = diag - off

        rows, cols = linear_sum_assignment(score, maximize=True)

        new_a = np.zeros_like(a)
        new_b = np.zeros_like(b)

        for row, col in zip(rows, cols):
            new_a[col] = a[row]
            new_b[col] = b[row]
        print (new_a)
        return new_a, new_b

    def to_canonical_iterative_form(self, a, b):
        n = len(a)

        c = np.zeros((n, n))
        d = np.zeros(n)

        for i in range(n):
            diag = a[i][i]
            if np.isclose(diag, 0):
                raise FailedPreprocessingStrategy()

            for j in range(n):
                if i == j:
                    c[i][j] = 0.0
                else:
                    c[i][j] = -a[i][j] / diag

            d[i] = b[i] / diag

        return c, d


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

        if not (self.is_diagonally_dominant(a)):
            a, b = self.to_dominant(a, b)

        an, bn = self.to_canonical_iterative_form(a, b)

        return an, bn


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