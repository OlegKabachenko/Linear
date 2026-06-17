__all__ = "BaseDialog, ErrorDialog"

import yaml
import os
import sys
from pathlib import Path

from kivy.lang import Builder

from kivy.uix.widget import Widget
from kivymd.uix.button import MDButton, MDButtonText
from kivymd.uix.dialog import MDDialog, MDDialogHeadlineText, MDDialogButtonContainer

from kivy.properties import StringProperty

from uix.mixins import SizableFontMixin
from uix.sizablebtn import SizableFabTextBtn

base_path = Path(sys._MEIPASS) if getattr(sys, 'frozen', False) else ""
config_path = os.path.join(base_path, 'uix', 'uix_config.yaml')
kv_path = os.path.join(base_path, "uix", "customdialog", "customdialog.kv")

with open(config_path, 'r') as file, \
        open(kv_path, encoding="utf-8") as kv_file:
    config = yaml.safe_load(file)
    Builder.load_string(kv_file.read())


class DialogText(MDDialogHeadlineText, SizableFontMixin):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        self.bind(text=self.update_text_font_size)
        self.bind(size=self.update_text_font_size)

    def update_text_font_size(self, instance, value):
        font = self.calculate_font(self.text, self.parent, min_font=config['DIALOG_MIN_FONT'],
                                   font_mlt_wide=config['DIALOG_FONT_MLT_WIDE'],
                                   font_mlt_narrow=config['DIALOG_FONT_MLT_NARROW'])
        self.font_size = font


class BaseDialog(MDDialog):
    head_text = StringProperty("")
    button_text = StringProperty("")
    bg_color = "black"  #if needed to change bg_color, add theme_bg_color = "Custom"
    text_color = "black"

    def __init__(self, head_text="Info", button_text="Ok", **kwargs):
        super().__init__(**kwargs)
        self.head_text = head_text
        self.button_text = button_text

    def calculate_btn_color(self, parent, delta=0.05):
        return [max(c - delta, 0) for c in parent.md_bg_color[:3]] + [parent.md_bg_color[3]]

    def set_head_text(self, text):
        self.head_text = text

    def set_button_text(self, text):
        self.button_text = text


class ErrorDialog(BaseDialog):
    theme_bg_color = "Custom"
    bg_color = config['ERROR_MSG_BG_COLOR']
    text_color = "red"
