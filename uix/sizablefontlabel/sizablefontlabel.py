__all__ = "SizableFontLabel"

from pathlib import Path
import yaml
import os
import sys
from pathlib import Path
from kivy.lang import Builder

from kivy.properties import NumericProperty

from kivymd.uix.label import MDLabel

from uix.mixins import SizableFontMixin

base_path = Path(sys._MEIPASS) if getattr(sys, 'frozen', False) else ""
config_path = os.path.join(base_path, 'uix', 'uix_config.yaml')
kv_path = os.path.join(base_path, "uix", "sizablefontlabel", "sizablefontlabel.kv")

with open(config_path, 'r', encoding="utf-8") as file, \
        open(kv_path, encoding="utf-8") as kv_file:
    config = yaml.safe_load(file)
    Builder.load_string(kv_file.read())


class SizableFontLabel(MDLabel, SizableFontMixin):
    min_font = NumericProperty(None)
    max_font = NumericProperty(None)
    font_mlt_wide = NumericProperty(None)
    font_mlt_narrow = NumericProperty(None)

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        self._font_properties = (
            "min_font",
            "max_font",
            "font_mlt_wide",
            "font_mlt_narrow",
        )

        for prop in self._font_properties:
            self.bind(**{prop: self._update_font})

        self.bind(
            width=self._update_font,
            text=self._update_font,
        )

    def _update_font(self, *args):
        font_kwargs = {
            prop: getattr(self, prop)
            for prop in self._font_properties
            if getattr(self, prop) is not None
        }

        self.font_size = self.calculate_font(
            self.text,
            self,
            **font_kwargs
        )

