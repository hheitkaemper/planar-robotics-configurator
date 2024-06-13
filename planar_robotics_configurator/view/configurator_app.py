from kivy import Config
from kivy.core.window import Window
from kivymd.app import MDApp
from kivymd.uix.gridlayout import MDGridLayout
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
        Window.size = (1600, 1200)
        screen = MDScreen()
        screen.theme_cls.theme_style = "Dark"
        screen.md_bg_color = "373737"
        self.layout = MDGridLayout(cols=1, orientation='lr-bt')
        nav = NavigationComponent(self)
        sim = SimulationComponent()
        nav.add_tab("Simulation", sim)
        nav.add_tab("Environment", EnvironmentComponent())
        self.layout.add_widget(nav)
        self.set_view(sim)
        screen.add_widget(self.layout)
        return screen

    def set_view(self, widget):
        if self.view is not None:
            self.layout.remove_widget(self.view)
        self.view = widget
        self.layout.add_widget(self.view, 1)
