from kivy.metrics import dp
from kivymd.uix.gridlayout import MDGridLayout

from planar_robotics_configurator.view.environment.environment_settings_dialog import EnvironmentSettingsDialog
from planar_robotics_configurator.view.utils import CustomIconButton, Divider
from planar_robotics_configurator.view.utils.custom_snackbar import CustomSnackbar


class EnvironmentSideBar(MDGridLayout):
    def __init__(self, env_component, **kwargs):
        super().__init__(**kwargs)
        self.env_component = env_component
        self.cols = 1
        self.md_bg_color = "#2F2F2F"
        self.padding = [dp(5), dp(5), dp(5), dp(5)]
        self.radius = [0, dp(10), dp(10), 0]
        self.spacing = [0, dp(5)]
        self.adaptive_size = True
        self.pos_hint = {"center_y": 0.5}
        self.add_widget(CustomIconButton(icon="crosshairs-gps",
                                         tooltip_text="Center map",
                                         on_release=lambda touch: self.env_component.map.center_map()))
        self.add_widget(CustomIconButton(icon="cog-outline",
                                         tooltip_text="Edit environment",
                                         on_release=lambda touch: self.open_settings()))
        self.add_widget(Divider(orientation="horizontal", width=dp(2), md_bg_color=(1, 1, 1, 1)))
        self.add_widget(CustomIconButton(icon="play",
                                         tooltip_text="Preview environment",
                                         on_release=lambda touch: self.env_component.show_preview()))

    def open_settings(self):
        """
        Opens the environment settings dialog if the current environment is not none.
        """
        if self.env_component.environment is None:
            CustomSnackbar(text="Please select an environment first!").open()
            return
        EnvironmentSettingsDialog(self.env_component, self.env_component.environment).open()
