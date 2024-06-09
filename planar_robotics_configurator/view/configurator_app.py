from kivymd.app import MDApp
from kivymd.uix.screen import MDScreen

from planar_robotics_configurator.view.environment.environment_component import EnvironmentComponent
from planar_robotics_configurator.view.navigation_component import NavigationComponent
from planar_robotics_configurator.view.simulation.simulation_component import SimulationComponent


class ConfiguratorApp(MDApp):
    def build(self):
        screen = MDScreen()
        screen.md_bg_color = "373737"
        nav = NavigationComponent()
        nav.add_tab("Simulation", SimulationComponent())
        nav.add_tab("Environment", EnvironmentComponent())
        screen.add_widget(nav)
        return screen
