__all__ = "BigTouchSwitch, ThemeSwitch, ParallelSwitch"

import os
import sys
from pathlib import Path

from kivy.properties import BooleanProperty, NumericProperty, StringProperty, ObjectProperty
from kivy.lang import Builder
from kivymd.icon_definitions import md_icons
from kivymd.uix.boxlayout import MDBoxLayout

from kivymd.app import MDApp

base_path = Path(sys._MEIPASS) if getattr(sys, 'frozen', False) else ""
kv_path = os.path.join(base_path, "uix", "bigtouchswitch", "bigtouchswitch.kv")

with open(
        kv_path, encoding="utf-8"
) as kv_file:
    Builder.load_string(kv_file.read())


class BigTouchSwitch(MDBoxLayout):
    active = BooleanProperty(False)
    disabled = BooleanProperty(False)
    switch_height = NumericProperty(34)
    switch_width = NumericProperty(80)
    icon_active = StringProperty("check")
    icon_inactive = StringProperty("close")
    on_active = ObjectProperty(lambda instance, value: None)

    def on_touch_down(self, touch):
        if not self.disabled:
            if self.collide_point(*touch.pos):
                self.active = not self.active
                return True
            return super().on_touch_down(touch)

    def on_touch_up(self, touch):
        if self.collide_point(*touch.pos):
            return True
        return super().on_touch_up(touch)


class ThemeSwitch(BigTouchSwitch):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        app = MDApp.get_running_app()
        app.register_theme_switch(self)

    def on_active(self, instance, value):
        MDApp.get_running_app().switch_theme_style(initiator=self)


class ParallelSwitch(BigTouchSwitch):
    pass
