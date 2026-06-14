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

