__all__ = ("BaseParamLayout, TextSlider, LimitParams")

import yaml
import os
import sys
from pathlib import Path
from kivy.lang import Builder

from kivy.core.window import Window

from kivy.properties import NumericProperty, StringProperty, BooleanProperty

from kivymd.uix.boxlayout import MDBoxLayout
from kivymd.uix.textfield import MDTextField
from kivymd.uix.widget import MDWidget
from kivymd.uix.slider import MDSlider, MDSliderHandle, MDSliderValueLabel
from kivymd.uix.label import MDLabel

from uix.mixins import SizableFontMixin


base_path = Path(sys._MEIPASS) if getattr(sys, 'frozen', False) else ""
config_path = os.path.join(base_path, 'uix', 'uix_config.yaml')
kv_path = os.path.join(base_path, "uix", "params", "params.kv")

with open(config_path, 'r') as file, \
        open(kv_path, encoding="utf-8") as kv_file:
    config = yaml.safe_load(file)
    Builder.load_string(kv_file.read())


class BaseParamLayout(MDBoxLayout):  #Base layout for function parameters
    h_height = NumericProperty(config['P_SECTION_HEIGHT'])
    is_animated = BooleanProperty(False)
    first_call = BooleanProperty(True)

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.height = self.h_height

    def on_kv_post(self, base_widget):
        self.is_animated = False
        self.first_call = True

    def orientation_check(self):
        v_height = len(self.children) * self.h_height

        screen_width = Window.width
        screen_height = Window.height
        critical_wdth = screen_width * config['APP_WIDE_SCR_MULT']

        if (critical_wdth > screen_height and self.height != self.h_height) or self.first_call:
            self.orientation = "horizontal"
            self.spacing = "60dp"
            if not self.is_animated:
                self.height = self.h_height

        elif (critical_wdth <= screen_height and self.height != v_height) or self.first_call:
            self.orientation = "vertical"
            self.spacing = "5sp"
            if not self.is_animated:
                self.height = v_height

        if self.first_call:
            self.first_call = False


class ParamLabel(MDLabel, SizableFontMixin):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.bind(size=self.update_text_font_size)

    def update_text_font_size(self, instance, value):
        font = self.calculate_font(self.text, self.parent, max_font=config['PRM_LBL_MAX_FONT'])
        self.font_size = font


class TextSlider(BaseParamLayout):
    title = StringProperty("Placeholder")
    min = NumericProperty(0)
    max = NumericProperty(100)
    value = NumericProperty(50)







