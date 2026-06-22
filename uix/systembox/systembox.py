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

            # Верхняя половина скобки
            Line(
                bezier=[
                    w_point + brace_width, h,
                    w_point, h - control_point_y_offset,
                    w_point + second_curve_x_offset, m - second_curve_y_offset,
                    w_point - center_notch_x, m,
                ],
                width=2
            )

            # Нижняя половина скобки
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
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        Clock.schedule_once(lambda dt: self.create_system(3)) #!!! Delete me

    def delete_system(self):
        self.ids.equations_box.clear_widgets()

    def create_system(self, n):
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

    def update_brace(self, dt=None):
        eq = self.ids.equations_box
        brace = self.ids.brace

        brace.height = eq.height

        print("brace height =", brace.height)
        print("brace width =", brace.width)
        print("brace pos =", brace.pos)

        brace.redraw()
