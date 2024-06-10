from kivy import Config
from kivymd.app import MDApp
from kivymd.uix.boxlayout import MDBoxLayout
from kivymd.uix.screen import MDScreen

from planar_robotics_configurator.view.environment.environment_component import EnvironmentComponent
from planar_robotics_configurator.view.navigation_component import NavigationComponent
from planar_robotics_configurator.view.simulation.simulation_component import SimulationComponent


class ConfiguratorApp(MDApp):

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.layout = None
        self.view = None

    def build(self):
        Config.set('input', 'mouse', 'mouse,disable_multitouch')
        screen = MDScreen()
        screen.md_bg_color = "373737"
        self.layout = MDBoxLayout(orientation='vertical')
        nav = NavigationComponent(self)
        nav.add_tab("Simulation", SimulationComponent())
        nav.add_tab("Environment", EnvironmentComponent())
        self.layout.add_widget(nav)
        self.set_view(SimulationComponent())
        screen.add_widget(self.layout)
        return screen

    def set_view(self, widget):
        if self.view is not None:
            self.layout.remove_widget(self.view)
        self.view = widget
        self.layout.add_widget(self.view)
        pass
