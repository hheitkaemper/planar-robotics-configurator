from kivymd.uix.floatlayout import MDFloatLayout
from kivymd.uix.label import MDLabel

from planar_robotics_configurator.view.environment.environment_map import EnvironmentMap


class EnvironmentComponent(MDFloatLayout):
    def __init__(self):
        super().__init__()
        self.size_hint = 1, 1
        self.add_widget(EnvironmentMap())
        self.add_widget(MDLabel(text='Environment Component', halign='center', valign='center'))
