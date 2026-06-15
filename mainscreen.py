__all__ = "MainScreen"

from pathlib import Path
import yaml
import os
import sys
from pathlib import Path
from kivy.lang import Builder
from kivymd.uix.screen import MDScreen
from uix.controlbox import SelectorBox
from tools.solver import Solver
from uix.bigtouchswitch import ThemeSwitch

base_path = Path(sys._MEIPASS) if getattr(sys, 'frozen', False) else ""
config_path = os.path.join(base_path, 'config.yaml')
kv_path = os.path.join(base_path, "mainscreen.kv")

with open(config_path, 'r', encoding="utf-8") as file, \
        open(kv_path, encoding="utf-8") as kv_file:
    config = yaml.safe_load(file)
    Builder.load_string(kv_file.read())


class MainScreen(MDScreen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self._init_methods()
        self._init_examples()
        self._init_selectors()


    def _init_methods(self):
        solver = Solver()
        self.METHODS = solver.METHODS
        self.METHOD_KEYS = list(self.METHODS.keys())
        #METHOD_VALUES = [info["function"] for info in METHODS.values()]


    def _init_examples(self):
        for key, value in config["EXAMPLES"].items():
            self._validate_exampls(key, value)

        self.EXAMPLES = {
            key: {
                "n": value["n"],
                "x": value["x"],
                "y": value["y"],
                "scale": value["scale"],
                "max_itr": value["max_itr"]
            }
            for key, value in config["EXAMPLES"].items()
        }

        self.EXAMPLE_KEYS = list(self.EXAMPLES.keys())

    def _init_selectors(self):
        self.ids.method_selector.items_list = self.METHOD_KEYS
        self.ids.example_selector.items_list = self.EXAMPLE_KEYS


    def _validate_exampls(self, key, value):
        if not key or not str(key).strip():
            raise ValueError("Example name can not be empty!")

        n = value["n"]
        x = value["x"]
        y = value["y"]
        scale = value["scale"]
        max_itr = value["max_itr"]

        if n is None:
            return

        self._validate_field("n", n, expected_type=int, min_val=1, max_val=30)
        self._validate_field("x", x, expected_type=list, length=n * n)
        self._validate_field("y", y, expected_type=list, length=n)
        self._validate_field("scale", scale, expected_type=int, min_val=1, max_val=110)
        self._validate_field("max_itr", max_itr, expected_type=int, min_val=1, max_val=300)

    def _validate_field(self, name, value, *, expected_type=None, min_val=None, max_val=None, length=None):

        if expected_type and not isinstance(value, expected_type):
            raise ValueError(f"Invalid type for {name}")

        if isinstance(value, (int, float)):
            if min_val is not None and value <= min_val:
                raise ValueError(f"{name} must be > {min_val}")
            if max_val is not None and value >= max_val:
                raise ValueError(f"{name} must be < {max_val}")

        if length is not None:
            if len(value) != length:
                raise ValueError(f"Invalid length for {name}")