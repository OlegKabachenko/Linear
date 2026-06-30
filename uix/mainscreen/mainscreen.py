__all__ = "MainScreen"

from pathlib import Path
import yaml
import os
import sys
from pathlib import Path
from kivy.lang import Builder

import time

from kivymd.uix.screen import MDScreen
from kivy.properties import NumericProperty
from kivy.clock import Clock
from kivymd.uix.boxlayout import MDBoxLayout

from tools.solver import Solver
from tools.system import System
from tools.solver import MaxIterationsExceeded

from uix.controlbox import SelectorBox
from uix.bigtouchswitch import ThemeSwitch, ParallelSwitch
from uix.standartboxlayout import StandartRootBox
from uix.restrictedscrollview import RestrictedScrollView
from uix.systemdatabox import SystemDataBox
from uix.customdialog import ErrorDialog
from uix.params import ClassicMethodsParam, DotsCntParam
from uix.sizablebtn import ExitBtn, SizableFabBtn


base_path = Path(sys._MEIPASS) if getattr(sys, 'frozen', False) else ""
config_path = os.path.join(base_path, 'uix', 'uix_config.yaml')
kv_path = os.path.join(base_path, "uix", "mainscreen", "mainscreen.kv")


with open(config_path, 'r', encoding="utf-8") as file, \
        open(kv_path, encoding="utf-8") as kv_file:
    config = yaml.safe_load(file)
    Builder.load_string(kv_file.read())


class MainScreen(MDScreen):
    current_method_id = NumericProperty(None)
    min_n = NumericProperty(None)
    max_n = NumericProperty(None)

    def __init__(self, app_config, **kwargs):
        super().__init__(**kwargs)
        self.app_config = app_config

        self._init_config()
        self._init_constants()
        self._init_examples()
        self._init_methods()
        self._init_widgets()
        self._init_selectors()

        Clock.schedule_once(self.init_params)

    def _init_config(self):
        self.ANIMATION_DURATION = self.app_config['ANIMATION_DURATION']
        self.DEFAULT_EXAMPLE_ID = self.app_config['DEFAULT_EXAMPLE_ID']
        self.DEFAULT_METHOD_ID = self.app_config['DEFAULT_METHOD_ID']

        self.min_n = self.app_config["MIN_N"]
        self.max_n = self.app_config["MAX_N"]
        self.min_scale = self.app_config["MIN_SCALE"]
        self.max_scale = self.app_config["MAX_SCALE"]
        self.min_max_itr = self.app_config["MIN_MAX_ITR"]
        self.max_max_itr = self.app_config["MAX_MAX_ITR"]
        self.min_eps = self.app_config["MIN_EPS"]
        self.max_eps = self.app_config["MAX_EPS"]

    def _init_constants(self):
        self.ROUND_PRECISION = config['ROUND_PRECISION']
        self.EXEC_TIME_PRECISION = config['EXEC_TIME_PRECISION']

    def _init_examples(self):
        self.primary_validate_examples()

        self.EXAMPLES = {
            key: {
                "system": System(
                    value.get("n"),
                    value.get("x"),
                    value.get("y")
                ) if value.get("n") is not None else None,
            }
            for key, value in self.app_config["EXAMPLES"].items()
        }

        self.EXAMPLE_KEYS = list(self.EXAMPLES.keys())
        self.EXAMPLE_VALUES = [
            example["system"] for example in self.EXAMPLES.values()
        ]

    def _init_methods(self):
        solver = Solver()
        self.METHODS = solver.METHODS
        self.METHOD_KEYS = list(self.METHODS.keys())
        self.METHOD_VALUES = [info["function"] for info in self.METHODS.values()]

    def _init_widgets(self):
        self.error_dialog = ErrorDialog()
        self.classic_methods_param = ClassicMethodsParam(
            min_scale=self.min_scale,
            max_scale=self.max_scale,
            min_itr=self.min_max_itr,
            max_itr=self.max_max_itr,
            min_eps=self.min_eps,
            max_eps=self.max_eps,
        )
        self.monte_param = DotsCntParam()

        self.extra_widgets = []
        self.extra_widgets_map = {
            "classic_methods_param": self.classic_methods_param,
            "monte_param": self.monte_param
        }
        self.set_extra_widgets()

    def _init_selectors(self):
        self.ids.example_selector.items_list = self.EXAMPLE_KEYS
        self.ids.method_selector.items_list = self.METHOD_KEYS

        self.ids.example_selector.default_element_id =self.DEFAULT_EXAMPLE_ID
        self.ids.method_selector.default_element_id = self.DEFAULT_METHOD_ID

        self.ids.example_selector.bind(on_select=lambda _, s_id, prev_id: self.handle_example_select(s_id, prev_id))
        self.ids.method_selector.bind(on_select=lambda _, s_id, prev_id: self.handle_method_select(s_id, prev_id))

    def primary_validate_examples(self):
        for key, value in self.app_config["EXAMPLES"].items():
            if not key or not str(key).strip():
                raise ValueError("Example name can not be empty!")

            n = value.get("n", None)

            if n is not None:
                if not (self.min_n <= n <= self.max_n):
                    raise ValueError(
                        f"N must be in range {self.min_n} - {self.max_n}, got {n}"
                    )

    def set_extra_widgets(self):
        for name, data in self.METHODS.items():
            widget_name = data.get("extra_widget")
            widget = self.extra_widgets_map.get(widget_name) if widget_name else None
            self.extra_widgets.append(widget)

    def init_params(self, _):
        self.current_method_id = self.DEFAULT_METHOD_ID
        self.handle_example_select(self.DEFAULT_EXAMPLE_ID, self.DEFAULT_EXAMPLE_ID + 1)
        self.handle_method_select(self.DEFAULT_METHOD_ID, self.DEFAULT_METHOD_ID + 1)

    def handle_example_select(self, s_id, prev_id):
        if s_id != prev_id:
            self.set_input_values(s_id)

    def handle_method_select(self, s_id, prev_id):
        if s_id != prev_id:
            self.manage_extra_method_params(s_id)
            self.manage_parallel_switch(s_id)
            self.current_method_id = s_id

    def manage_extra_method_params(self, i):
        self.ids.systemdatabox.add_extra_params(self.extra_widgets[i], self.ANIMATION_DURATION)

    def manage_parallel_switch(self, i):
        parallel_swicth = self.ids.parallel_switch

        if self.METHODS[self.METHOD_KEYS[i]]["can_be_parallel"] is True:
            parallel_swicth.disabled = False
        else:
            parallel_swicth.active = False
            parallel_swicth.disabled = True

    def set_input_values(self, i):
        system = self.EXAMPLE_VALUES[i]

        if system is not None:
            n = system.get_n()
            x = system.get_x()
            y = system.get_y()

            self.ids.systemdatabox.set_system_data(n, x, y)
        else:
            n = None
            self.ids.systemdatabox.delete_system()

        self.ids.systemdatabox.set_system_size(n)

    def get_current_method(self):
        return self.METHOD_VALUES[self.current_method_id]

    def get_system_roots(self):
        params = self.ids.systemdatabox.get_system_params()
        if params is None:
            self.show_error("Будь ласка, правильно заповніть поля!")
            return

        system, extra_params = params
        method = self.get_current_method()

        self.call_solver(system, method, **extra_params)

        #result, exec_time = self.call_solver(system, method, **extra_params)

    def call_solver(self, system: System, method, **kwargs):
        try:
            start_time = time.time()
            result = method(system, kwargs)
            end_time = time.time()

            exec_time = end_time - start_time

            return result, exec_time
        except MaxIterationsExceeded:
            self.show_error("Перевищено максимальну кількість ітерацій, спробуйте збільшити цей параметр!")


    def show_error(self, text):
        self.error_dialog.set_head_text(text)
        self.error_dialog.open()