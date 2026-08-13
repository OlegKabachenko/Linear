__all__ = "CalculateBox"

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

    def show_result(self, x, deltas, itr, exec_time):
        fnm_big = config['RES_LBL_FMN_BIG']
        precision = config['LBL_ROUND_PRECISION']

        self._add_label("Знайдений розв'язок", bold=True, font_mlt_narrow=fnm_big)

        for i, value in enumerate(x, start=1):
            self._add_label(f"x{i} = {value:.{precision}f}")

        self._add_label("Похибки отриманих розв'язків", bold=True, font_mlt_narrow=fnm_big)

        for i, delta in enumerate(deltas, start=1):
            self._add_label(f"Δ{i} = {delta:.{precision}f}")

        self._add_label(f"Кількість ітерацій: {itr}", bold=True, font_mlt_narrow=fnm_big)
        self._add_label(f"Час виконання: {exec_time:.{precision}f} с", bold=True, font_mlt_narrow=fnm_big)


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

    def calculate_roots(self, system, method, extra_params, is_parallel):
        self.clear_output()

        self._show_indicator()
        Thread(
            target=self._solve_worker,
            args=(system, method, extra_params, is_parallel),
            daemon=True
        ).start()

    def _solve_worker(self, system, method, extra_params, is_parallel):
        try:
            result = self.call_solver(system, method, is_parallel, **extra_params)

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

    def _on_solver_finished(self, system, result):
        if result is None:
            return

        x, itr, exec_time = result
        deltas = system.verify_solution(x)

        self.ids.result_box.show_result(x, deltas, itr, exec_time)

    def call_solver(self, system: System, method, is_parallel, **kwargs):
        start_time = time.time()

        result, itr = method(system, kwargs, is_parallel)
        end_time = time.time()

        exec_time = end_time - start_time
        return result, itr, exec_time

