__all__ = ("BaseParamLayout", "DotsCntParam", "IntParam", "FloatParam", "SizeParam", "ClassicMethodsParam")

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

import matplotlib.pyplot as plt

from sympy import Symbol, sympify, SympifyError
from re import findall, match

from uix.mixins import SizableFontMixin

from kivy_garden.matplotlib.backend_kivyagg import FigureCanvasKivyAgg

base_path = Path(sys._MEIPASS) if getattr(sys, 'frozen', False) else ""
config_path = os.path.join(base_path, 'uix', 'uix_config.yaml')
kv_path = os.path.join(base_path, "uix", "params", "params.kv")

with open(config_path, 'r') as file, \
        open(kv_path, encoding="utf-8") as kv_file:
    config = yaml.safe_load(file)
    Builder.load_string(kv_file.read())


class ParameterText(MDTextField, SizableFontMixin):
    is_required = True

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.font = 16

        mock_widget = MDWidget()  # Create a mock widget since the mixin requires an MDWidget instance
        mock_widget.width = mock_widget.height = self.height

        self.bind(size=lambda instance, value: setattr(self, 'font_size', self.calculate_font(
            self.text, self, root_width_mlt=config['BTN_ROOT_WIDTH_MLT'], height_based_font=True,
            height_font_mlt=config['P_HEIGHT_FONT_MLT'])))

    def set_error(self, item, is_error=True):
        item.error = is_error
        return


class StrictParameterText(ParameterText):
    forbid_negative = BooleanProperty(False)

    def insert_text(self, substring, from_undo=False):
        if self.forbid_negative:
            substring = substring.replace("-", "")
        return super().insert_text(substring, from_undo)


class BaseParamLayout(MDBoxLayout):  #Base layout for function parameters
    h_height = NumericProperty(config['P_SECTION_HEIGHT'])
    is_animated = BooleanProperty(False)
    first_call = BooleanProperty(True)
    hint = StringProperty()
    forbid_negative_param = BooleanProperty(False)

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.height = self.h_height

    def on_kv_post(self, base_widget):
        self.is_animated = False
        self.first_call = True

    def set_params(self, **kwargs):
        for key, value in kwargs.items():
            if key in self.ids:
                self.ids[key].text = value

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

    def get_params(self, widget=None, result=None):
        if widget is None:
            widget = self
        if result is None:
            result = {}

        ids_dict = widget.ids.items()

        for key, value in ids_dict:
            if isinstance(value, MDTextField):
                result[key] = self.get_param_text(value)
            self.get_params(value, result)

        return result

    def get_param_text(self, widget):
        if widget.error:
            raise ValueError(f"Widget is in error state!")
        else:
            return widget.text


class StandartParam(BaseParamLayout):
    input_type = StringProperty()

    def set_params(self, value):
        self.ids.input.text = "" if value is None else str(value)


class IntParam(StandartParam):  #Integer parameter
    input_type = 'int'

    def get_params(self, **kwargs):
        return int(self.get_param_text(self.ids.input))


class FloatParam(StandartParam):
    input_type = 'float'

    def get_params(self, **kwargs):
        return float(self.get_param_text(self.ids.input))


class ClassicMethodsParam(BaseParamLayout):
    def set_params(self, scale, limit):
        self.ids.scale.text = scale
        self.ids.limit.text = limit

    def get_params(self, **kwargs):
        result = {
            "scale": self.get_param_text(self.ids.scale),
            "limit": self.get_param_text(self.ids.limit)
        }
        return result


class SizeParam(IntParam):
    forbid_negative_param = True
    hint = "Розмірність системи"


class DotsCntParam(IntParam):
    forbid_negative_param = True
    hint = "Кількість точок"
