from kivymd.uix.floatlayout import MDFloatLayout

from planar_robotics_configurator.model.configurator_model import ConfiguratorModel
from planar_robotics_configurator.model.environment import Environment
from planar_robotics_configurator.view.environment.map import EnvironmentMap
from planar_robotics_configurator.view.environment.selection import EnvironmentSelection
from planar_robotics_configurator.view.environment.side_bar import EnvironmentSideBar
from planar_robotics_configurator.view.utils import Component, CustomSnackbar


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
        self.selection: EnvironmentSelection = EnvironmentSelection(self)
        self.add_widget(self.selection)
        self.add_widget(EnvironmentSideBar(self))

    def on_select(self, _):
        if self.environment is not None:
            return
        if len(ConfiguratorModel().environments) == 0:
            return
        self.environment = ConfiguratorModel().environments[0]
        self.set_environment(self.environment)

    def set_environment(self, environment: Environment):
        self.environment = environment
        if environment is None:
            self.selection.set_text("None")
            self.map.reset()
        else:
            self.selection.set_text(environment.name)
            self.map.set_environment(environment)


    def show_preview(self):
        if self.environment is None:
            CustomSnackbar(text="Please select an environment first!").open()
            return
        try:
            self.environment.create_basic_planar_robotics_env().render()
        except Exception as e:
            if len(e.args) > 0:
                CustomSnackbar(text=e.args[0]).open()
            else:
                CustomSnackbar(text="An exception occupied while trying to create a preview rendering!").open()
