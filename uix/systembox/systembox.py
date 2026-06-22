import yaml
import os
import sys
from pathlib import Path
from kivy.lang import Builder

from kivymd.uix.boxlayout import MDBoxLayout
from kivy.clock import Clock
from kivy.metrics import sp
from kivymd.uix.label import MDLabel
from kivy.properties import NumericProperty
from kivy.uix.widget import Widget
from kivy.graphics import Line, Color, Rectangle, Bezier

import numpy as np

import time

from uix.restrictedscrollview import RestrictedScrollView
from uix.params import SystemFloatParam

base_path = Path(sys._MEIPASS) if getattr(sys, 'frozen', False) else ""
config_path = os.path.join(base_path, 'uix', 'uix_config.yaml')
kv_path = os.path.join(base_path, "uix", "systembox", "systembox.kv")

with open(config_path, 'r') as file, \
        open(kv_path, encoding="utf-8") as kv_file:
    config = yaml.safe_load(file)
    Builder.load_string(kv_file.read())


class SystemBrace(Widget):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.bind(pos=self.redraw, size=self.redraw)

    def redraw(self, *args):
        self.canvas.clear()

        center_shift_x = 20
        top_bottom_margin = 10

        control_point_y_offset = 3

        brace_width = 40
        center_notch_x = 15

        second_curve_x_offset = 35
        second_curve_y_offset = 6

        w_point = self.center_x - center_shift_x
        h = self.height - top_bottom_margin
        m = h / 2

        with self.canvas:
            Color(0, 0, 0, 1)

            # Upper half of the bracket
            Line(
                bezier=[
                    w_point + brace_width, h,
                    w_point, h - control_point_y_offset,
                    w_point + second_curve_x_offset, m - second_curve_y_offset,
                    w_point - center_notch_x, m,
                ],
                width=2
            )

            # Lower half of the bracket
            Line(
                bezier=[
                    w_point + brace_width, top_bottom_margin,
                    w_point, top_bottom_margin - control_point_y_offset,
                    w_point + second_curve_x_offset, m + second_curve_y_offset,
                    w_point - center_notch_x, m,
                ],
                width=2
            )


class SystemLabel(MDLabel):
    font = NumericProperty()

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.font = sp(config['SYSTEM_FONT'])


class SystemRow(MDBoxLayout):
    pass


class SystemBox(MDBoxLayout):
    def delete_system(self):
        self.ids.equations_box.clear_widgets()

    def create_system(self, n):
        start = time.perf_counter()
        equations_box = self.ids.equations_box

        self.delete_system()

        for i in range(n):
            row = SystemRow()

            for j in range(n):
                row.add_widget(SystemFloatParam())
                row.add_widget(
                    SystemLabel(
                        text=f"x[sub]{j + 1}[/sub]" + (" +" if j < n - 1 else ""),
                        markup=True
                    )
                )

            row.add_widget(SystemLabel(text="="))
            row.add_widget(SystemFloatParam())
            row.add_widget(SystemLabel(text=f"y[sub]{i + 1}[/sub]", markup = True))

            equations_box.add_widget(row)

        Clock.schedule_once(self.update_brace)
        end = time.perf_counter()
        print(f"create_system execution time: {end - start:.6f} sec")

    def update_brace(self, *args):
        self.ids.brace.redraw()

    def change_size(self, new_n):
        start = time.perf_counter()
        new_n = int(new_n)
        if new_n <= 1:
            return

        x, y = self.get_data()

        x = np.asarray(x, dtype=float)
        y = np.asarray(y, dtype=float)

        old_n = x.shape[0] if x.size else 0

        new_x = np.zeros((new_n, new_n), dtype=float)
        new_y = np.zeros(new_n, dtype=float)

        n_min = min(old_n, new_n)

        if old_n > 0:
            new_x[:n_min, :n_min] = x[:n_min, :n_min]
            new_y[:n_min] = y[:n_min]

        self.create_system(new_n)
        self.set_data(new_x, new_y)

        end = time.perf_counter()
        print(f"change_size execution time: {end - start:.6f} sec")

    def get_data(self):
        equations_box = self.ids.equations_box

        x_arr = []
        y_arr = []

        rows = equations_box.children[::-1]

        for row in rows:
            float_widgets = [w for w in row.children if isinstance(w, SystemFloatParam)][::-1]

            x_row = []
            for i in range(len(float_widgets) - 1):
                x_row.append(float_widgets[i].get_params())

            y_val = float_widgets[-1].get_params()

            x_arr.append(x_row)
            y_arr.append(y_val)

        x_arr = np.array(x_arr, dtype=float)
        y_arr = np.array(y_arr, dtype=float)

        return x_arr, y_arr

    def set_data(self, x_arr, y_arr):
        equations_box = self.ids.equations_box
        rows = equations_box.children[::-1]

        x_arr = np.asarray(x_arr)
        y_arr = np.asarray(y_arr)

        n = min(len(rows), x_arr.shape[0])

        for i in range(n):
            row = rows[i]

            float_widgets = [w for w in row.children if isinstance(w, SystemFloatParam)][::-1]

            m = min(len(float_widgets) - 1, x_arr.shape[1])

            for j in range(m):
                float_widgets[j].set_params(x_arr[i, j])

            float_widgets[-1].set_params(y_arr[i])


