import numpy as np
from gymnasium_planar_robotics.envs.basic_envs import BasicPlanarRoboticsEnv
from kivymd.uix.floatlayout import MDFloatLayout

from planar_robotics_configurator.model.configurator_model import ConfiguratorModel
from planar_robotics_configurator.model.environment.environment import Environment
from planar_robotics_configurator.view.environment.environment_map import EnvironmentMap
from planar_robotics_configurator.view.environment.environment_selection import EnvironmentSelection
from planar_robotics_configurator.view.environment.environment_side_bar import EnvironmentSideBar
from planar_robotics_configurator.view.utils import Component
from planar_robotics_configurator.view.utils.custom_snackbar import CustomSnackbar


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
        self.map.set_environment(self.environment)

    def set_environment(self, environment: Environment):
        self.environment = environment
        self.map.set_environment(environment)
        self.selection.set_text(environment.name)

    def show_preview(self):
        if self.environment is None:
            CustomSnackbar(text="Please select an environment first!").open()
            return
        try:
            # TODO insert actual movers. At moment one mover because rendering need a minimum of one mover.
            preview_env = BasicPlanarRoboticsEnv(
                layout_tiles=self.environment.tiles,
                num_movers=1,
                tile_params={
                    "mass": self.environment.tile_mass,
                    "size": np.array([
                        self.environment.tile_width / 100,
                        self.environment.tile_length / 100,
                        self.environment.tile_height / 100
                    ])
                },
                table_height=self.environment.table_height / 100,
                std_noise=self.environment.std_noise,
                initial_mover_start_xy_pos=np.array([[0.48, 0.48]]),
                use_mj_passive_viewer=True)
            preview_env.render()
        except Exception as e:
            if len(e.args) > 0:
                CustomSnackbar(text=e.args[0]).open()
            else:
                CustomSnackbar(text="An exception occupied while trying to create a preview rendering!").open()
