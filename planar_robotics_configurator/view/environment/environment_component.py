from kivymd.uix.floatlayout import MDFloatLayout

from planar_robotics_configurator.model.configurator_model import ConfiguratorModel
from planar_robotics_configurator.model.environment.environment import Environment
from planar_robotics_configurator.view.environment.environment_map import EnvironmentMap
from planar_robotics_configurator.view.environment.environment_selection import EnvironmentSelection
from planar_robotics_configurator.view.environment.environment_side_bar import EnvironmentSideBar
from planar_robotics_configurator.view.utils import Component


class EnvironmentComponent(MDFloatLayout, Component):
    """
    The layout for the environment site.
    """

    def __init__(self):
        super().__init__()
        self.size_hint = 1, 1
        self.environment: Environment | None = None
        self.map = EnvironmentMap()
        self.add_widget(self.map)
        self.add_widget(EnvironmentSelection(self))
        self.add_widget(EnvironmentSideBar(self))

    def on_select(self, _):
        if self.environment is not None:
            return
        if len(ConfiguratorModel().environments) == 0:
            return
        self.environment = ConfiguratorModel().environments[0]
        self.map.set_environment(self.environment)

    def set_environment(self, environment: Environment):
        self.environment = environment
        self.map.set_environment(environment)
