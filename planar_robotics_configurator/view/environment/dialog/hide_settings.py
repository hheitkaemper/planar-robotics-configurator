from kivy.metrics import dp
from kivymd.uix.boxlayout import MDBoxLayout

from planar_robotics_configurator.view.utils import ScrollDialog, CustomCheckbox, CustomLabel


class HideSettings(ScrollDialog):
    """
    Dialog for change the visibility of elements on the environment map.
    """

    def __init__(self, env_map):
        self.env_map = env_map
        self.hide_list = []
        super().__init__("Hide Settings", "Cancel", "Confirm")
        self.add_option("environment_background", "Show Environment Background")
        self.add_option("tiles", "Show Tiles")
        self.add_option("movers", "Show Movers")
        self.add_option("movers_collision", "Show Movers Collision", indent=1)
        self.add_option("working_stations", "Show Working Stations")
        self.add_option("working_stations_name", "Show Working Stations Name", indent=1)
        self.add_option("objects", "Show Objects")
        self.add_option("objects_name", "Show Objects Name", indent=1)

    def on_confirm(self):
        for hide in self.hide_list:
            self.env_map.hiding_settings[hide] = self.__dict__[hide]
        self.env_map.redraw()
        self.dismiss()

    def on_cancel(self):
        self.dismiss()

    def add_option(self, att, text, indent=0):
        self.hide_list.append(att)
        self.__dict__[att] = self.env_map.hiding_settings[att]
        layout = MDBoxLayout(orientation="horizontal", adaptive_height=True, spacing=dp(20))
        layout.padding[0] = dp(40*indent)
        checkbox = CustomCheckbox(size_hint=(None, None), width=dp(20), height=dp(20),
                                  pos_hint={"center_y": 0.5}, active=self.__dict__[att])
        checkbox.bind(on_release=lambda instance: self.__setattr__(att, instance.active))
        layout.add_widget(checkbox)
        layout.add_widget(CustomLabel(text=text, pos_hint={"center_y": 0.5}))
        self.add_scroll_widget(layout)
