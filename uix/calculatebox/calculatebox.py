__all__ = "CalculateBox"

import numpy as np
from numpy.linalg import LinAlgError

import time

import yaml
from pathlib import Path
import os
import sys
from pathlib import Path
from kivy.lang import Builder

from threading import Thread
from kivy.clock import Clock
from kivy.metrics import dp
from kivy.graphics import Color, Rectangle

from kivymd.uix.boxlayout import MDBoxLayout
from kivymd.uix.loadingindicator import MDLoadingIndicator
from kivymd.uix.label import MDLabel
from kivy.properties import NumericProperty

from uix.restrictedscrollview import RestrictedScrollView
from uix.sizablebtn import SizableFabBtn
from uix.mixins import SizableFontMixin

from tools.solver import MaxIterationsExceeded
from tools.preprocessing import FailedPreprocessingStrategy
from tools.system import System
from tools.solverresultinfo import SolverResultInfo


base_path = Path(sys._MEIPASS) if getattr(sys, 'frozen', False) else ""
config_path = os.path.join(base_path, 'uix', 'uix_config.yaml')
kv_path = os.path.join(base_path, "uix", "calculatebox", "calculatebox.kv")

with open(config_path, 'r') as file, \
     open(kv_path, encoding="utf-8") as kv_file:
    config = yaml.safe_load(file)
    Builder.load_string(kv_file.read())

class ResultLabel(MDLabel, SizableFontMixin):
    font_mlt_narrow = NumericProperty(config['RES_LBL_FMN'])

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        self.bind(
            size=self._update_font,
            text=self._update_font
        )

    def _update_font(self, *args):
        self.font_size = self.calculate_font(
            self.text,
            font_mlt_narrow=self.font_mlt_narrow,

            max_font=config['RES_LBL_MAX_FONT'],
            min_font=config['RES_LBL_MIN_FONT']
        )


class ResultBox(MDBoxLayout):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    def _add_label(self, text, bold=False, font_mlt_narrow=config['RES_LBL_FMN']):
        self.add_widget(
            ResultLabel(
                text=text,
                bold=bold,
                font_mlt_narrow=font_mlt_narrow,
            )
        )

    def show_result(self, extra_info: SolverResultInfo):
        fnm_big = config['RES_LBL_FMN_BIG']
        precision = config['LBL_ROUND_PRECISION']

        for info in sorted(
                extra_info.values(),
                key=lambda entry: entry["order"]
        ):
            value = info["value"]
            label = info["label"]
            bold = info["bold"]
            item_label = info["item_label"]
            suffix = info["value_suffix"]
            value_format = info["value_format"]

            font_mlt_narrow = (
                fnm_big if bold else config['RES_LBL_FMN']
            )

            if np.isscalar(value):
                if value_format == "int":
                    text = f"{label}: {value}{suffix}"
                else:
                    text = f"{label}: {value:.{precision}f}{suffix}"

                self._add_label(
                    text,
                    bold=bold,
                    font_mlt_narrow=font_mlt_narrow
                )

            else:
                self._add_label(
                    label,
                    bold=bold,
                    font_mlt_narrow=font_mlt_narrow
                )

                for i, element in enumerate(value, start=1):
                    if value_format == "int":
                        text = f"{element}{suffix}"
                    else:
                        text = f"{element:.{precision}f}{suffix}"

                    if item_label is not None:
                        text = f"{item_label}{i} = {text}"

                    self._add_label(text)


class CalculateBox(MDBoxLayout):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.register_event_type("on_calculate")
        self.register_event_type("on_error")

    def on_button_press(self):
        self.dispatch("on_calculate")

    def on_calculate(self):
        pass

    def on_error(self, message):
        pass

    def _show_indicator(self):
        self.ids.indicator_box.height = max(self.height * 0.4, dp(60))
        self.ids.indicator_box.opacity = 1
        self.ids.indicator.start()

    def _hide_indicator(self):
        self.ids.indicator.stop()
        self.ids.indicator_box.opacity = 0
        self.ids.indicator_box.height = 0

    def clear_output(self):
        if self.ids.result_box.children:
            self.ids.result_box.clear_widgets()

    def calculate_roots(self, system, method, extra_params):
        self.clear_output()

        self._show_indicator()
        Thread(
            target=self._solve_worker,
            args=(system, method, extra_params),
            daemon=True
        ).start()

    def _solve_worker(self, system, method, extra_params):
        try:
            result = self.call_solver(system, method, **extra_params)

            Clock.schedule_once(
                lambda dt: self._on_solver_finished(system, result)
            )

        except MaxIterationsExceeded:
            Clock.schedule_once(
                lambda dt: self.dispatch(
                    "on_error",
                    "Перевищено максимальну кількість ітерацій, спробуйте збільшити цей параметр!"
                )
            )

        except LinAlgError:
            Clock.schedule_once(
                lambda dt: self.dispatch(
                    "on_error",
                    "Матриця вироджена, неможливо застосувати передобробку!"
                )
            )

        except FailedPreprocessingStrategy:
            Clock.schedule_once(
                lambda dt: self.dispatch(
                    "on_error",
                    "Не вдалося виконати передобробку, спробуйте іншу!"
                )
            )

        finally:
            Clock.schedule_once(lambda dt: self._hide_indicator())

    def _on_solver_finished(self, system: System, result):
        if result is None:
            return

        resultinfo, exec_time, = result
        x = resultinfo["solution"]["value"]

        resultinfo.add_deltas(system.verify_solution(x))
        resultinfo.add_exec_time(exec_time)

        self.ids.result_box.show_result(resultinfo)

    def call_solver(self, system: System, method, **kwargs):
        start_time = time.time()

        result = method(system, kwargs)

        end_time = time.time()

        exec_time = end_time - start_time
        return result, exec_time

