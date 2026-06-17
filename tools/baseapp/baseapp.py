__all__ = "BaseApp"

from kivymd.app import MDApp


class BaseApp(MDApp):
    def __init__(self, screen_class, custom_sfce_cnt_hg_clr, **kwargs):
        super().__init__(**kwargs)
        self.app_config = None
        self.MULTI_SCREEN = False
        self.main_screen = None
        self._screen_class = screen_class
        self.custom_surfaceContainerHighestColor = custom_sfce_cnt_hg_clr
        self._switch_in_progress = False
        self.theme_sync_switches = []

    def switch_theme_style(self, initiator=None):
        if self._switch_in_progress:
            return

        self._switch_in_progress = True

        self.theme_cls.theme_style = "Dark" if self.theme_cls.theme_style == "Light" else "Light"
        if self.theme_cls.theme_style == "Light":
            self.theme_cls.surfaceContainerHighestColor = self.custom_surfaceContainerHighestColor

        #if app have multiple theme_switch, synchronize their state
        for theme_switch in self.theme_sync_switches:
            if theme_switch is not initiator:
                theme_switch.active = not theme_switch.active

        self._switch_in_progress = False

    def register_theme_switch(self, switch):
        self.theme_sync_switches.append(switch)

    def build(self):
        self.theme_cls.theme_style = "Light"
        self.theme_cls.primary_palette = "Azure"
        self.theme_cls.surfaceContainerHighestColor = self.custom_surfaceContainerHighestColor
        self.main_screen = self._screen_class(self.app_config)
        return self.main_screen
