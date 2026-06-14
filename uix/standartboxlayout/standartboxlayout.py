__all__ = "StandartBox, StandartSelectSection, StandartRootBox, StandartResultBox"

import os
import sys
from pathlib import Path
from kivy.lang import Builder

from kivymd.uix.boxlayout import MDBoxLayout

base_path = Path(sys._MEIPASS) if getattr(sys, 'frozen', False) else ""
kv_path = os.path.join(base_path, "uix", "standartboxlayout", "standartboxlayout.kv")

with open(
        kv_path, encoding="utf-8"
) as kv_file:
    Builder.load_string(kv_file.read())


class StandartRootBox(MDBoxLayout):
    pass


class StandartBox(MDBoxLayout):
    pass


class StandartSelectSection(StandartBox):
    pass

