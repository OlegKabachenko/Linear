class PreprocessingStrategy:
    key = None
    label = None

    def process(self, data, params=None):
        raise NotImplementedError


class Preconditioning(PreprocessingStrategy):
    key = "prec"
    label = "Попереднє кондиціонування"

    def process(self, data, params=None):
        return data


class Spectral(PreprocessingStrategy):
    key = "spectral"
    label = "Спектральний критерій"

    def process(self, data, params=None):
        return data


class NonePreprocessing(PreprocessingStrategy):
    key = "none"
    label = "Без передобробки"

    def process(self, data, params=None):
        return data


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