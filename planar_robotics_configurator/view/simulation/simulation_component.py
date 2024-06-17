from kivymd.uix.boxlayout import MDBoxLayout
from kivymd.uix.label import MDLabel

from planar_robotics_configurator.view.utils import Component


class SimulationComponent(MDBoxLayout, Component):
    def __init__(self):
        super().__init__()
        self.add_widget(MDLabel(text='Simulation Component', halign='center'))

    def on_select(self, _):
        pass