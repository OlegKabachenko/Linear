__all__ = "SystemDataBox"

import os
import sys
from pathlib import Path
from kivy.lang import Builder

from kivymd.uix.boxlayout import MDBoxLayout
from kivy.properties import NumericProperty

from tools.animation import Animator

from uix.parameterbox import ParameterBox
from uix.params import SizeParamExtra
from uix.systembox import SystemBox
from uix.restrictedscrollview import NestedHorizontalScrollView

base_path = Path(sys._MEIPASS) if getattr(sys, 'frozen', False) else ""
kv_path = os.path.join(base_path, "uix", "systemdatabox", "systemdatabox.kv")

with open(
        kv_path, encoding="utf-8"
) as kv_file:
    Builder.load_string(kv_file.read())


class SystemDataBox(MDBoxLayout):
    animator = Animator()
    min_size = NumericProperty(None)
    max_size = NumericProperty(None)

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.register_event_type("on_system_changed")

    def on_system_changed(self):
        pass

    def get_system_params(self):
        extra_params_box = self.ids.extra_params_box
        extra_params = {}

        if self.ids.size_param.is_error():
            return None

        try:

            system = self.ids.system.get_data()

            if extra_params_box.children:
                for child in extra_params_box.children:
                    extra_params.update(child.get_params())

            return system, extra_params

        except ValueError:
            return None

    def change_system_size(self, n):
        self.ids.system.change_size(n)
        self.dispatch("on_system_changed")

    def set_system_size(self, size):
        self.ids.size_param.set_params(size)

    def clear_system_data(self):
        self.ids.system.clear_data()
        self.dispatch("on_system_changed")

    def set_system_data(self, n, x, y):
        self.ids.system.create_system(n)
        self.ids.system.set_data(x, y)

    def add_params(self, parent_id, params_widget, duration):
        parent_box = self.ids[parent_id]

        if params_widget is not None and params_widget not in parent_box.children:
            self.animator.animate_container_clear(parent_box, duration)
            self.animator.animate_widget_add(parent_box, params_widget, duration)

    def add_extra_params(self, extra_params, duration):
        if extra_params is None:
            self.delete_extra_params(duration)
        else:
            self.add_params("extra_params_box", extra_params, duration)

    def delete_extra_params(self, delete_duration):
        self.animator.animate_container_clear(self.ids.extra_params_box, delete_duration)