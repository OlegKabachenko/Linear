__all__ = "SizableFabTextBtn, SizableFabBtn, ExitBtn"

import yaml
import os
import sys
from pathlib import Path
from kivy.lang import Builder

from kivymd.uix.button import MDFabButton
from kivymd.uix.button import MDExtendedFabButton
from kivymd.app import MDApp
from kivy.properties import StringProperty, ColorProperty
from kivymd.icon_definitions import md_icons

from uix.mixins import SizableFontMixin

base_path = Path(sys._MEIPASS) if getattr(sys, 'frozen', False) else ""
config_path = os.path.join(base_path, 'uix', 'uix_config.yaml')
kv_path = os.path.join(base_path, "uix", "sizablebtn", "sizablebtn.kv")

with open(config_path, 'r') as file, \
        open(kv_path, encoding="utf-8") as kv_file:
    config = yaml.safe_load(file)
    Builder.load_string(kv_file.read())


class SizableFabBtn(MDFabButton, SizableFontMixin):
    custom_light_icon_color = ColorProperty("white")

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        self.bind(size=lambda instance, value: setattr(self, 'font_size', self.calculate_font(
            self.text, self, root_width_mlt=config['BTN_ROOT_WIDTH_MLT'], max_font=150)))

    def on_kv_post(self, base_widget):
        self.update_icon_color()

        app = MDApp.get_running_app()
        app.theme_cls.bind(theme_style=self.on_theme_change)

    def on_theme_change(self, instance, value):
        self.update_icon_color()

    def update_icon_color(self):
        app = MDApp.get_running_app()

        if app.theme_cls.theme_style == "Light":
            self.theme_icon_color = "Custom"
            self.icon_color = self.custom_light_icon_color

        else:
            self.theme_icon_color = "Primary"


class ExitBtn(SizableFabBtn):
    def exit(self):
        app = MDApp.get_running_app()
        if getattr(app, 'MULTI_SCREEN', True):
            if getattr(app, 'main_screen'):
                if app.main_screen.current == "main":
                    app.stop()
                else:
                    app.main_screen.current = "main"
        else:
            app.stop()


class SizableFabTextBtn(MDExtendedFabButton, SizableFontMixin):
    button_text = StringProperty("")
    text_color = ColorProperty()

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.bind(button_text=self.update_button_text)
        self.bind(size=self.update_text_font_size)

    def update_button_text(self, instance, value):
        self.ids.text.text = value

    def update_text_font_size(self, instance, value):
        if 'text' in self.ids:
            font = self.calculate_font(
                self.ids.text.text, self, root_width_mlt=config['BTN_ROOT_WIDTH_MLT'])
            self.ids.text.font_size = font
