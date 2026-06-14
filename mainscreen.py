__all__ = "MainScreen"

from pathlib import Path
import yaml
import os
import sys
from pathlib import Path
from kivy.lang import Builder
from kivymd.uix.screen import MDScreen

base_path = Path(sys._MEIPASS) if getattr(sys, 'frozen', False) else ""
config_path = os.path.join(base_path, 'config.yaml')
kv_path = os.path.join(base_path, "mainscreen.kv")

with open(config_path, 'r') as file, \
        open(kv_path, encoding="utf-8") as kv_file:
    config = yaml.safe_load(file)
    Builder.load_string(kv_file.read())


class MainScreen(MDScreen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)