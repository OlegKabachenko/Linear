import yaml
import os
import sys
from pathlib import Path
from kivy.lang import Builder

from kivymd.app import MDApp
from kivymd.uix.boxlayout import MDBoxLayout
from kivy.clock import Clock
from kivy.metrics import sp, dp
from kivymd.uix.label import MDLabel
from kivymd.uix.textfield import MDTextField
from kivy.properties import NumericProperty
from kivy.uix.widget import Widget
from kivy.graphics import Line, Color, Rectangle, Bezier

import numpy as np

import time

from uix.restrictedscrollview import RestrictedScrollView
from tools.system import System

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

        self.app = MDApp.get_running_app()
        self.app.theme_cls.bind(theme_style=self.redraw)

    def get_brace_color(self):
        if self.app.theme_cls.theme_style == "Dark":
            return (1, 1, 1, 1)
        else:
            return (0, 0, 0, 1)

    def redraw(self, *args):
        self.canvas.clear()

        center_shift_x = 20
        top_bottom_margin = 2

        control_point_y_offset = 3

        brace_width = 40
        center_notch_x = 15

        second_curve_x_offset = 35
        second_curve_y_offset = 6

        w_point = self.center_x - center_shift_x
        h = self.height - top_bottom_margin
        m = h / 2

        color = self.get_brace_color()

        with self.canvas:
            Color(*color)

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


class SystemCoef(MDTextField):
    pass


class SystemRow(MDBoxLayout):
    pass


class SystemBox(MDBoxLayout):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.register_event_type("on_data_change")

    def on_data_change(self):
        pass

    def delete_system(self):
        equations_box = self.ids.equations_box

        for row in equations_box.children:
            row.clear_widgets()

        equations_box.clear_widgets()

    def add_element(self, row, widget, index=None):
        if index is None:
            row.add_widget(widget)
        else:
            row.add_widget(widget, index=index)

    def create_cell(self, row, i, n, is_x: bool, index=None):
        float_param = SystemCoef()
        float_param.bind(text=lambda *_: self.dispatch("on_data_change"))
        float_param.text = "0"

        if is_x:
            self.add_element(row,float_param,index)

            label = SystemLabel(
                    text=f"x[sub]{i + 1}[/sub]" + (" +" if i < n - 1 else ""),
                    markup=True
                )

            self.add_element(row, label, index)

        else:
            self.add_element(row, SystemLabel(text="="), index)
            self.add_element(row, float_param, index)
            label = SystemLabel(text=f"y[sub]{i + 1}[/sub]", markup=True)
            self.add_element(row, label, index)

    def create_row(self, n, i, box):
        row = SystemRow()
        for j in range(n):
            self.create_cell(row, j, n, True)
        self.create_cell(row, i, n, False)

        box.add_widget(row)

    def change_last_x_lbl_in_row(self, row, i, x_num, need_plus: bool):
        label = row.children[i]

        label.text = (
            f"x[sub]{x_num + 1}[/sub] +"
            if need_plus else
            f"x[sub]{x_num + 1}[/sub]"
        )

    def create_system(self, n):
        if n is None:
            return

        equations_box = self.ids.equations_box

        self.delete_system()

        for i in range(n):
            self.create_row(n, i, equations_box)

        Clock.schedule_once(self.update_brace)

    def update_brace(self, *args):
        self.ids.brace.redraw()

    def clear_data(self):
        equations_box = self.ids.equations_box

        for row in equations_box.children:
            for widget in row.children:
                if isinstance(widget, SystemCoef):
                    widget.text = "0"

    def change_size(self, new_n):

        try:
            new_n = int(new_n)
        except (TypeError, ValueError):
            return

        if new_n <= 1:
            return

        equations_box = self.ids.equations_box
        rows = list(equations_box.children)
        old_n = len(rows)

        if not rows:
            self.create_system(new_n)
            return

        if new_n == old_n:
            return

        delta = abs(new_n - old_n)

        equations_box = self.ids.equations_box
        rows = list(equations_box.children)

        tail_widget_cnt = 3

        if old_n < new_n:
            for row in rows:
                self.change_last_x_lbl_in_row(row, tail_widget_cnt, old_n - 1, True)

            for i in range(delta):
                x_idx = old_n + i

                for row in rows:
                    self.create_cell(row, x_idx, new_n, True, tail_widget_cnt)

                self.create_row(new_n, x_idx, equations_box)
        else:
            widgets_in_cell = 2
            count = delta * widgets_in_cell

            removed_rows = rows[:delta]
            for row in removed_rows:
                row.clear_widgets()

            equations_box.clear_widgets(children=removed_rows)

            for row in equations_box.children:
                removed_cells = row.children[tail_widget_cnt:tail_widget_cnt + count]
                row.clear_widgets(children=removed_cells)
                self.change_last_x_lbl_in_row(row, tail_widget_cnt, new_n - 1, False)

    def get_data(self):
        equations_box = self.ids.equations_box

        rows = equations_box.children[::-1]
        n = len(rows)

        x_arr = np.zeros((n, n), dtype=float)
        y_arr = np.zeros(n, dtype=float)

        for i, row in enumerate(rows):
            widgets = [w for w in row.children if isinstance(w, SystemCoef)][::-1]

            for j in range(len(widgets) - 1):
                x_arr[i, j] = float(widgets[j].text)

            y_arr[i] = float(widgets[-1].text)

        return System(n, x_arr, y_arr)

    def set_data(self, x_arr, y_arr):
        equations_box = self.ids.equations_box
        rows = equations_box.children[::-1]

        x_arr = np.asarray(x_arr)
        y_arr = np.asarray(y_arr)

        n = min(len(rows), x_arr.shape[0])

        for i in range(n):
            row = rows[i]

            widgets = [w for w in row.children if isinstance(w, SystemCoef)][::-1]

            m = min(len(widgets) - 1, x_arr.shape[1])

            for j in range(m):
                widgets[j].text = str(x_arr[i, j])
            widgets[-1].text = str(y_arr[i])



