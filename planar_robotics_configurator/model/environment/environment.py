from dataclasses import dataclass, field
import numpy as np
from gymnasium_planar_robotics.envs.basic_envs import BasicPlanarRoboticsEnv

from planar_robotics_configurator.model.environment.mover import Mover
from planar_robotics_configurator.model.environment.object import Object, RefObject, CubeObject, BallObject
from planar_robotics_configurator.model.environment.working_station import WorkingStation


@dataclass(frozen=False)
class Environment:
    """
    Represents a planar robotics environment.
    :param name: Name of the environment. Used to identify the environment.
    :param num_width: Width number of tiles for the environment in x direction.
    :param num_length: Length number of tiles for the environment in y direction.
    :param tiles: [num_width, num_length] Array of int. 1 for a tile at the position, 0 else
    :param tile_width: width (cm) of the tiles in the environment in x direction.
    :param tile_length: length (cm) of the tiles in the environment in y direction.
    :param tile_height: height (cm) of the tiles in the environment in z direction.
    :param tile_mass: mass (kg) of the tiles in the environment.
    :param table_height: height (cm) of the table in the environment.
    :param std_noise: Standard deviation of the noise in the environment.
    :param movers: List of movers in the environment.
    :param working_stations: List of working stations in the environment.
    :param objects: List of objects in the environment.
    """
    name: str
    num_width: int
    num_length: int
    tiles: np.ndarray = field(init=False)
    tile_width: float
    tile_length: float
    tile_height: float
    tile_mass: float
    initial_mover_zpos: float
    table_height: float
    std_noise: float
    movers: list[Mover] = field(default_factory=list)
    working_stations: list[WorkingStation] = field(default_factory=list)
    objects: list[Object] = field(default_factory=list)

    def __post_init__(self):
        self.init_tiles()

    def init_tiles(self):
        """
        Creates the tiles of the environment.
        Sets all tiles to zero, which represents a not existing tile.
        """
        self.tiles = np.zeros((self.num_width, self.num_length), dtype=int)

    def update_tiles(self):
        """
        Updates the tiles array. Expands or slices the current tiles to create an array matching the needed size.
        """
        if self.num_width != self.tiles.shape[0]:
            if self.num_width < self.tiles.shape[0]:
                self.tiles = self.tiles[:self.num_width, :]
            else:
                self.tiles = np.concatenate(
                    (self.tiles, np.zeros((self.num_width - self.tiles.shape[0],
                                           self.tiles.shape[1]), dtype=int)), axis=0)
        if self.num_length != self.tiles.shape[1]:
            if self.num_length < self.tiles.shape[1]:
                self.tiles = self.tiles[:, :self.num_length]
            else:
                self.tiles = np.concatenate((
                    self.tiles, np.zeros((self.tiles.shape[0],
                                          self.num_length - self.tiles.shape[1]), dtype=int)), axis=1)

    def set_size(self, num_width: int, num_length: int):
        """
        Sets the size of the environment and updates the tiles array.
        """
        self.num_width = num_width
        self.num_length = num_length
        self.movers[:] = [m for m in self.movers if m.x < num_width and m.y < num_length]
        self.update_tiles()

    def get_tile(self, x, y) -> bool:
        """
        Gets a tile at position x, y in the tile coordinate-system.
        :param x: x coordinate of the tile.
        :param y: y coordinate of the tile.
        """
        return self.tiles[x, y]

    def set_tile(self, x, y, value):
        """
        Sets the value of a tile at position x, y in the tile coordinate-system.
        :param x: x coordinate of the tile.
        :param y: y coordinate of the tile.
        :param value: value of the tile, this value should only be 0 for not existing and 1 for existing tile.
        """
        assert value in [0, 1]
        self.tiles[x, y] = value

    def create_basic_planar_robotics_env(self, passive_viewer=True) -> BasicPlanarRoboticsEnv:
        """
        Create an environment with all the environment settings.
        """
        custom_model_xml_strings = {
            "custom_outworldbody_xml_str": self.create_outworldbody_xml_str()
        }
        env = BasicPlanarRoboticsEnv(
            layout_tiles=self.tiles,
            num_movers=len(self.movers),
            tile_params={
                "mass": self.tile_mass,
                "size": np.array([self.tile_width / 2, self.tile_length / 2, self.tile_height / 2
                                  ])
            },
            mover_params={
                "size": np.array(list(map(lambda mover: [mover.preset.width / 2,
                                                         mover.preset.length / 2,
                                                         mover.preset.height / 2], self.movers)))
            },
            table_height=self.table_height,
            std_noise=self.std_noise,
            initial_mover_start_xy_pos=np.array(list(
                map(lambda mover: [(mover.x + 0.5) * self.tile_width,
                                   (mover.y + 0.5) * self.tile_length],
                    self.movers))),
            custom_model_xml_strings=custom_model_xml_strings,
            use_mj_passive_viewer=passive_viewer)
        return env

    def create_outworldbody_xml_str(self) -> str:
        import tempfile
        import xml.etree.ElementTree as ET
        import os
        mp_xml_str = ""
        for working_station in self.working_stations:
            dirname, basename = os.path.split(working_station.fileRef)
            tmp = tempfile.NamedTemporaryFile(delete=False, prefix=basename, dir=dirname)
            et = ET.parse(working_station.fileRef)
            body = et.find("worldbody").find("body")
            body.attrib["pos"] = (f'{working_station.position[0]} {working_station.position[1]} '
                                  f'{working_station.position[2]}')
            et.write(tmp.name)
            mp_xml_str += f'\n\t<include file="{tmp.name}"/>'
        for object_instance in self.objects:
            if isinstance(object_instance, RefObject):
                dirname, basename = os.path.split(object_instance.fileRef)
                tmp = tempfile.NamedTemporaryFile(delete=False, prefix=basename, dir=dirname)
                et = ET.parse(object_instance.fileRef)
                body = et.find("worldbody").find("body")
                body.attrib["pos"] = (f'{object_instance.position[0]} {object_instance.position[1]} '
                                      f'{object_instance.position[2]}')
                et.write(tmp.name)
                mp_xml_str += f'\n\t<include file="{tmp.name}"/>'
            if isinstance(object_instance, CubeObject):
                root = ET.Element("worldbody")
                body = ET.SubElement(root, "body")
                geom = ET.SubElement(body, "geom")
                geom.attrib["type"] = "box"
                geom.attrib["pos"] = (f'{object_instance.position[0]} {object_instance.position[1]} '
                                      f'{object_instance.position[2]}')
                geom.attrib["size"] = (f'{object_instance.width / 2} {object_instance.length / 2} '
                                       f'{object_instance.height / 2}')
                mp_xml_str += f'\n\t{ET.tostring(root)}'
            if isinstance(object_instance, BallObject):
                root = ET.Element("worldbody")
                body = ET.SubElement(root, "body")
                geom = ET.SubElement(body, "geom")
                geom.attrib["type"] = "sphere"
                geom.attrib["pos"] = (f'{object_instance.position[0]} {object_instance.position[1]} '
                                      f'{object_instance.position[2]}')
                geom.attrib["size"] = f'{object_instance.radius}'
                mp_xml_str += f'\n\t{ET.tostring(root)}'
        return mp_xml_str

    def to_config(self):
        config = {}
        config['width'] = self.num_width
        config['length'] = self.num_length
        config['tiles'] = "".join(str(x) for x in self.tiles.reshape(self.num_width * self.num_length))
        config['tile_width'] = self.tile_width / 2
        config['tile_length'] = self.tile_length / 2
        config['tile_height'] = self.tile_height / 2
        config['tile_mass'] = self.tile_mass
        config['initial_mover_zpos'] = self.initial_mover_zpos
        config['table_height'] = self.table_height
        config['std_noise'] = self.std_noise
        config['num_movers'] = len(self.movers)
        mover_config = {}
        for idx, mover in enumerate(self.movers):
            mover_config[idx] = mover.to_config(self.tile_width, self.tile_length)
        config['movers'] = mover_config
        config['num_objects'] = len(self.objects)
        objects_config = {}
        for idx, obj in enumerate(self.objects):
            objects_config[idx] = obj.to_config()
        config['objects'] = objects_config
        config['num_working_stations'] = len(self.working_stations)
        working_stations_config = {}
        for idx, working_station in enumerate(self.working_stations):
            working_stations_config[idx] = working_station.to_config()
        config['working_stations'] = working_stations_config
        return config

    @staticmethod
    def from_config(name, config):
        environment = Environment(name=name, num_width=config["width"], num_length=config["length"],
                                  tile_width=config["tile_width"] * 2, tile_length=config["tile_length"] * 2,
                                  tile_height=config["tile_height"] * 2, tile_mass=config["tile_mass"],
                                  initial_mover_zpos=config["initial_mover_zpos"], table_height=config["table_height"],
                                  std_noise=config["std_noise"])
        environment.tiles = np.array([int(x) for x in config["tiles"]]).reshape((environment.num_width,
                                                                                 environment.num_length))
        for x in range(config["num_movers"]):
            mover_config = config["movers"][x]
            environment.movers.append(Mover.from_config(mover_config, environment.tile_width, environment.tile_length))
        for x in range(config["num_working_stations"]):
            working_station_config = config["working_stations"][x]
            environment.working_stations.append(WorkingStation.from_config(str(x), working_station_config))
        for x in range(config["num_objects"]):
            object_config = config["objects"][x]
            if object_config["type"] == "ref":
                environment.objects.append(RefObject.from_config(str(x), object_config))
            if object_config["type"] == "cube":
                environment.objects.append(CubeObject.from_config(str(x), object_config))
            if object_config["type"] == "sphere":
                environment.objects.append(BallObject.from_config(str(x), object_config))
        return environment
