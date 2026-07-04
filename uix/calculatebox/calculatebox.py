__all__ = "CalculateBox"

from numpy.linalg import LinAlgError

import time

from pathlib import Path
import os
import sys
from pathlib import Path
from kivy.lang import Builder

from threading import Thread
from kivy.clock import Clock
from kivy.metrics import dp

from kivymd.uix.boxlayout import MDBoxLayout
from kivymd.uix.loadingindicator import MDLoadingIndicator
from kivymd.uix.label import MDLabel

from uix.restrictedscrollview import RestrictedScrollView
from uix.sizablebtn import SizableFabBtn

from tools.solver import MaxIterationsExceeded
from tools.preprocessing import FailedPreprocessingStrategy
from tools.system import System


base_path = Path(sys._MEIPASS) if getattr(sys, 'frozen', False) else ""
kv_path = os.path.join(base_path, "uix", "calculatebox", "calculatebox.kv")


with open(kv_path, encoding="utf-8") as kv_file:
    Builder.load_string(kv_file.read())


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

    def calculate_roots(self, system, method, extra_params, is_parallel):
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


    def call_solver(self, system: System, method, is_parallel, **kwargs):

        start_time = time.time()

        result, itr = method(system, kwargs, is_parallel)
        end_time = time.time()

        exec_time = end_time - start_time
        return result, itr, exec_time
