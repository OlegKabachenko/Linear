__all__ = "RestrictedScrollView", "NestedHorizontalScrollView"

import os
import sys
from pathlib import Path
from kivy.lang import Builder

from kivy.uix.scrollview import ScrollView


class RestrictedScrollView(ScrollView):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    def on_scroll_y(self, instance, value):
        if value > 1:
            self.scroll_y = 1
        return value

    def on_touch_down(self, touch):
        super().on_touch_down(touch)

    def on_touch_move(self, touch):
        super().on_touch_move(touch)

    def on_touch_up(self, touch):
        super().on_touch_up(touch)


class NestedHorizontalScrollView(RestrictedScrollView):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.do_scroll_x = True
        self.do_scroll_y = False

    def on_scroll_move(self, touch):
        super().on_scroll_move(touch)
        touch.ud['sv.handled']['y'] = False