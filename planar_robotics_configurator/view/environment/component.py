import numpy as np
from gymnasium_planar_robotics.envs.basic_envs import BasicPlanarRoboticsEnv
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
        self.map.set_environment(environment)
        self.selection.set_text(environment.name)

    def show_preview(self):
        if self.environment is None:
            CustomSnackbar(text="Please select an environment first!").open()
            return
        try:
            mp_xml_str = ""
            for working_station in self.environment.working_stations:
                import tempfile
                import xml.etree.ElementTree as ET
                tmp = tempfile.NamedTemporaryFile(delete=False)
                et = ET.parse(working_station.fileRef)
                body = et.find("worldbody").find("body")
                body.attrib["pos"] = (f'{working_station.position[0] / 100} {working_station.position[1] / 100} '
                                      f'{working_station.position[2] / 100}')
                et.write(tmp.name)
                mp_xml_str += f'\n\t<include file="{tmp.name}"/>'
            custom_model_xml_strings = {
                "custom_outworldbody_xml_str": mp_xml_str
            }
            preview_env = BasicPlanarRoboticsEnv(
                layout_tiles=self.environment.tiles,
                num_movers=len(self.environment.movers),
                tile_params={
                    "mass": self.environment.tile_mass,
                    "size": np.array([
                        self.environment.tile_width / 200,
                        self.environment.tile_length / 200,
                        self.environment.tile_height / 200
                    ])
                },
                mover_params={
                    "size": np.array(list(map(lambda mover: [mover.preset.width / 200,
                                                             mover.preset.length / 200,
                                                             mover.preset.height / 200], self.environment.movers)))
                },
                table_height=self.environment.table_height / 100,
                std_noise=self.environment.std_noise,
                initial_mover_start_xy_pos=np.array(list(
                    map(lambda mover: [(mover.x + 0.5) * (self.environment.tile_width / 100),
                                       (mover.y + 0.5) * (self.environment.tile_length / 100)],
                        self.environment.movers))),
                custom_model_xml_strings=custom_model_xml_strings,
                use_mj_passive_viewer=True)
            preview_env.render()
        except Exception as e:
            if len(e.args) > 0:
                CustomSnackbar(text=e.args[0]).open()
            else:
                CustomSnackbar(text="An exception occupied while trying to create a preview rendering!").open()
