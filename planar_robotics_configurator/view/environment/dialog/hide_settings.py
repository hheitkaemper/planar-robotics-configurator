from kivy.metrics import dp
from kivymd.uix.boxlayout import MDBoxLayout

from planar_robotics_configurator.view.utils import ScrollDialog, CustomCheckbox, CustomLabel


class HideSettings(ScrollDialog):
    """
    Dialog for change the visibility of elements on the environment map.
    """

    def __init__(self, env_map):
        self.env_map = env_map
        super().__init__("Hide Settings", "Cancel", "Confirm")
        self.show_env_background = env_map.hiding_settings["environment_background"]
        self.add_option("Show Environment Background", self.show_env_background,
                        lambda instance: self.__setattr__("show_env_background", instance.active))
        self.show_tiles = env_map.hiding_settings["tiles"]
        self.add_option("Show Tiles", self.show_tiles,
                        lambda instance: self.__setattr__("show_tiles", instance.active))
        self.show_movers = env_map.hiding_settings["movers"]
        self.add_option("Show Movers", self.show_movers,
                        lambda instance: self.__setattr__("show_movers", instance.active))
        self.show_movers_collision = env_map.hiding_settings["movers_collision"]
        self.add_option("Show Movers Collision", self.show_movers_collision,
                        lambda instance: self.__setattr__("show_movers_collision", instance.active))
        self.show_working_stations = env_map.hiding_settings["working_stations"]
        self.add_option("Show Working Stations", self.show_working_stations,
                        lambda instance: self.__setattr__("show_working_stations", instance.active))

    def on_confirm(self):
        self.env_map.hiding_settings["environment_background"] = self.show_env_background
        self.env_map.hiding_settings["tiles"] = self.show_tiles
        self.env_map.hiding_settings["movers"] = self.show_movers
        self.env_map.hiding_settings["movers_collision"] = self.show_movers_collision
        self.env_map.hiding_settings["working_stations"] = self.show_working_stations
        self.env_map.redraw()
        self.dismiss()

    def on_cancel(self):
        self.dismiss()

    def add_option(self, text, active, callback):
        layout = MDBoxLayout(orientation="horizontal", adaptive_height=True, spacing=dp(20))
        checkbox = CustomCheckbox(size_hint=(None, None), width=dp(20), height=dp(20),
                                  pos_hint={"center_y": 0.5}, active=active)
        checkbox.bind(on_release=callback)
        layout.add_widget(checkbox)
        layout.add_widget(CustomLabel(text=text, pos_hint={"center_y": 0.5}))
        self.add_scroll_widget(layout)
