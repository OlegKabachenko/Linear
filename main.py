from pathlib import Path
import yaml
import os
import sys
from kivy.lang import Builder
from tools.baseapp import BaseApp

from uix.standartboxlayout import StandartRootBox
from uix.restrictedscrollview import RestrictedScrollView
from mainscreen import MainScreen

base_path = Path(sys._MEIPASS) if getattr(sys, 'frozen', False) else ""
config_path = os.path.join(base_path, 'config.yaml')

with open(config_path, 'r', encoding="utf-8") as file:
    config = yaml.safe_load(file)


class LinearApp(BaseApp):
    def __init__(self, **kwargs):
        super().__init__(MainScreen, config['CARD_L_COLOR'], **kwargs)

    def build(self):
        super().build()
        return self.main_screen


if __name__ == "__main__":
    LinearApp().run()