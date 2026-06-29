__all__ = ("BaseParamLayout", "StandartParam", "IntParam", "FloatParam", "ClassicMethodsParam", "SizeParam", "DotsCntParam", "SizeParamExtra", "SystemFloatParam")

import yaml
import os
import sys
from pathlib import Path
from kivy.lang import Builder

from kivy.core.window import Window
from kivy.clock import Clock
from kivy.properties import NumericProperty, StringProperty, BooleanProperty, ObjectProperty
from kivy.metrics import dp

from kivy_garden.matplotlib.backend_kivyagg import FigureCanvasKivyAgg
from kivymd.uix.boxlayout import MDBoxLayout
from kivymd.uix.textfield import MDTextField
from kivymd.uix.widget import MDWidget

import matplotlib.pyplot as plt

from sympy import Symbol, sympify, SympifyError
from re import findall, match

from uix.mixins import SizableFontMixin
from uix.sizablebtn import SizableFabBtn
from uix.customdialog import ErrorDialog
from uix.bigtouchswitch import BigTouchSwitch
from uix.controlbox import SelectorBox

from tools.preprocessing import registry


base_path = Path(sys._MEIPASS) if getattr(sys, 'frozen', False) else ""
config_path = os.path.join(base_path, 'uix', 'uix_config.yaml')
kv_path = os.path.join(base_path, "uix", "params", "params.kv")

with open(config_path, 'r') as file, \
        open(kv_path, encoding="utf-8") as kv_file:
    config = yaml.safe_load(file)
    Builder.load_string(kv_file.read())


class ParameterText(MDTextField, SizableFontMixin):
    is_required = True
    forbid_negative = BooleanProperty(False)
    min_value = NumericProperty(None)
    max_value = NumericProperty(None)
    can_be_zero = BooleanProperty(False)
    _internal_update = BooleanProperty(False)

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.font = 16

        mock_widget = MDWidget()  # Create a mock widget since the mixin requires an MDWidget instance
        mock_widget.width = mock_widget.height = self.height

        self.bind(size=lambda instance, value: setattr(self, 'font_size', self.calculate_font(
            self.text, self, root_width_mlt=config['BTN_ROOT_WIDTH_MLT'], height_based_font=True,
            height_font_mlt=config['P_HEIGHT_FONT_MLT'])))

    def on_text(self, instance, value):
        if self._internal_update is True:
            return

        try:
            num = float(value)
        except ValueError:
            return

        if self.min_value is not None and num < self.min_value:
            Clock.schedule_once(lambda dt: self.set_error(self), 0)

        if self.max_value is not None and num > self.max_value:
            Clock.schedule_once(lambda dt: self.set_error(self), 0)

        if not self.can_be_zero and value == "0":
            self._internal_update = True
            Clock.schedule_once(lambda dt: setattr(instance, "text", ""), 0)
            Clock.schedule_once(lambda dt: setattr(self, "_internal_update", False), 0)

    def insert_text(self, substring, from_undo=False):
        if self.forbid_negative:
            substring = substring.replace("-", "")
        return super().insert_text(substring, from_undo)

    def set_error(self, item, is_error=True):
        item.error = is_error
        return


class BaseParamLayout(MDBoxLayout):  #Base layout for function parameters
    h_height = NumericProperty(config['P_SECTION_HEIGHT'])
    is_animated = BooleanProperty(False)
    first_call = BooleanProperty(True)
    hint = StringProperty()
    forbid_negative_param = BooleanProperty(False)

    _pending_update = BooleanProperty(False)

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
            self.spacing = "5dp"
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
    min_value = NumericProperty(None)
    max_value = NumericProperty(None)
    value = StringProperty()

    def is_error(self):
        return self.ids.input.error

    def has_error(self):
        return self.ids.input.error

    def set_params(self, value):
        self.ids.input.text = "" if value is None else str(value)


class IntParam(StandartParam):
    input_type = 'int'

    def get_params(self, **kwargs):
        return int(self.get_param_text(self.ids.input))


class FloatParam(StandartParam):
    input_type = 'float'

    def get_params(self, **kwargs):
        return float(self.get_param_text(self.ids.input))


class SystemFloatParam(FloatParam):
    def on_kv_post(self, base_widget):
        field = self.ids.input

        field.can_be_zero = True
        field.ids.hint_text.text = ""

        self.size_hint_x = None
        self.width = dp(config['INPUT_FIELD_WIDTH'])
        field.width = self.width

        field.height = dp(config['INPUT_FIELD_HEIGHT'])


class PreconditionParams(BaseParamLayout):
    min_scale = NumericProperty(None)
    max_scale = NumericProperty(None)
    min_itr = NumericProperty(None)
    max_itr = NumericProperty(None)

    def set_params(self, scale, limit):
        self.ids.scale.text = scale
        self.ids.limit.text = limit

    def get_params(self, **kwargs):
        result = {
            "scale": self.ids.scale.get_params(),
            "limit": self.ids.limit.get_params()
        }
        return result


class ClassicMethodsParam(BaseParamLayout):
    min_scale = NumericProperty(None)
    max_scale = NumericProperty(None)
    min_itr = NumericProperty(None)
    max_itr = NumericProperty(None)

    current_p_method_id = NumericProperty(None)
    default_p_method_id = config['DEFAULT_P_MTD_ID']

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self._init_selector()

    def _init_selector(self):
        selector = self.ids.precondition_mtd

        self.current_p_method_id = self.default_p_method_id
        selector.default_element_id = self.default_p_method_id

        selector.items_list = [label for _, label in registry.items()]

        selector.bind(on_select=lambda _, s_id, prev_id: self.handle_p_method_select(s_id, prev_id))

        self.handle_p_method_select(self.default_p_method_id, -9)

    def handle_p_method_select(self, s_id, prev_id):
        if s_id == prev_id:
            return

        strategy = registry.get_by_id(s_id)

        self.current_p_method_id = s_id

        precondition_params = self.ids.precondition_params

        precondition_params.opacity = 1 if strategy.key == "prec" else 0

    def orientation_check(self):
        screen_width = Window.width
        screen_height = Window.height
        critical_wdth = screen_width * config['APP_WIDE_SCR_MULT']

        if critical_wdth > screen_height and self.height != self.h_height:
            self.spacing = "0dp"
        else:
            self.spacing = "10sp"

        Clock.schedule_once(self._update_height, 0)

    def _update_height(self, dt):
        if not self.is_animated:
            total_height = sum(child.height for child in self.children)

            spacing = self.spacing if isinstance(self.spacing, (int, float)) else self.spacing[1]
            total_height += spacing * max(0, len(self.children))
            total_height += self.padding[1] + self.padding[3]

            self.height = total_height

    def set_params(self, scale, limit):
        self.ids.precondition_params.set_params(scale, limit)

    def get_params(self, **kwargs):
        strategy = registry.get_by_id(self.current_p_method_id)
        key = strategy.key

        if key == "prec":
            result = self.ids.precondition_params.get_params()
        else:
            result = {"scale": 0, "limit": 0}

        result["p_type"] = key

        return result


class SizeParam(IntParam):
    forbid_negative_param = True
    hint = "Розмірність системи"


class DotsCntParam(IntParam):
    forbid_negative_param = True
    hint = "Кількість точок"


class SizeParamExtra(BaseParamLayout):
    min_value = NumericProperty(None)
    max_value = NumericProperty(None)
    value = ObjectProperty(None, allownone=True)

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.register_event_type("on_apply")

    def _on_inner_value(self, value):
        try:
            self.value = float(value)
        except ValueError:
            self.value = None

    def orientation_check(self):
        super().orientation_check()
        if self.orientation == "horizontal":
            self.spacing = "10dp"
            self.ids.size_box.size_hint = (0.6, 1)
            self.ids.buttons_box.size_hint = (0.4, 1)
            self.set_bottom_padding(0)

            for btn in self.ids.buttons_box.children:
                btn.size_hint = (1, 0.7)

        else:
            self.spacing = "0dp"
            self.ids.size_box.size_hint = (1, 1)
            self.ids.buttons_box.size_hint = (1, 1)
            self.set_bottom_padding("20dp")

            for btn in self.ids.buttons_box.children:
                btn.size_hint = (1, 0.75)

    def set_bottom_padding(self, value):
        p = self.padding
        self.padding = (p[0], p[1], p[2], value)

    def set_params(self, n):
        self.ids.size_param.set_params(n)

    def increment(self):
        self._change_value(1)
        self.dispatch_apply_action()

    def decrement(self):
        self._change_value(-1)
        self.dispatch_apply_action()

    def dispatch_apply_action(self):
        if not self.ids.size_param.has_error():
            self.dispatch("on_apply", self.value)
        else:
            a = ErrorDialog(
                f"Значення має бути від {self.min_value} до {self.max_value}."
            )
            a.open()

    def on_apply(self, value):
        pass

    def is_error(self):
        return self.ids.size_param.is_error()

    def _change_value(self, delta):
        widget = self.ids.size_param

        try:
            value = float(widget.ids.input.text or 0)
        except ValueError:
            raise ValueError(f"Exception during value change in sizeparam:'{text}'")

        new_value = value + delta

        if self.min_value is not None:
            new_value = max(self.min_value, new_value)

        if self.max_value is not None:
            new_value = min(self.max_value, new_value)

        widget.ids.input.text = str(int(new_value))