__all__ = "SizableFontMixin"

import yaml
import os
import sys
from pathlib import Path

from kivy.core.window import Window
import math

from kivymd.uix.widget import MDWidget

base_path = Path(sys._MEIPASS) if getattr(sys, 'frozen', False) else ""
config_path = os.path.join(base_path, 'uix', 'uix_config.yaml')

with open(config_path, 'r') as file:
    config = yaml.safe_load(file)


class SizableFontMixin:
    def calculate_font(self, text: str, root: MDWidget = Window, root_width_mlt: float = config['APP_WIDE_SCR_MULT'],
                       font_mlt_wide: float = config['FONT_MLT_WIDE'],
                       font_mlt_narrow: float = config['FONT_MLT_NARROW'],
                       height_based_font: bool = False, height_font_mlt: float = config['HEIGHT_FONT_MLT'],
                       max_font: int = config['MAX_FONT'], min_font: int = config['MIN_FONT']):

        root_width = root.width
        root_height = root.height

        if not height_based_font:
            text_len = len(text) + 1  #to prevent /0

            if root_width * root_width_mlt > root_height:
                font = (root_width * font_mlt_wide) / text_len
                font = min(root_height, font)
            else:
                font = ((root_width * font_mlt_narrow) / text_len)

        else:
            font = root_height * height_font_mlt

        font = max(min_font, font)
        font = min(max_font, font)

        return f"{font}sp"
