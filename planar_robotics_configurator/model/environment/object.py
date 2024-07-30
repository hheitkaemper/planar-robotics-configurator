from dataclasses import dataclass
from typing import Tuple


@dataclass(frozen=False)
class Object:
    name: str
    position: Tuple[float, float, float]
    color: Tuple[float, float, float, float]

    def to_config(self):
        raise NotImplementedError()

    @staticmethod
    def from_config(name, config):
        raise NotImplementedError()


@dataclass(frozen=False)
class RefObject(Object):
    fileRef: str

    def to_config(self):
        config = {
            "type": "ref",
            "x": self.position[0],
            "y": self.position[1],
            "z": self.position[2]
        }
        config["ref"] = self.fileRef
        return config

    @staticmethod
    def from_config(name, config):
        return RefObject(name=name, fileRef=config["ref"], position=(config["x"], config["y"], config["z"]),
                         color=(1, 1, 1, 1))


@dataclass(frozen=False)
class CubeObject(Object):
    width: float
    length: float
    height: float
    friction: float

    def to_config(self):
        config = {
            "type": "cube",
            "x": self.position[0],
            "y": self.position[1],
            "z": self.position[2]
        }
        config["width"] = self.width / 2
        config["length"] = self.length / 2
        config["height"] = self.height / 2
        return config

    @staticmethod
    def from_config(name, config):
        return CubeObject(name=name, width=config["width"], length=config["length"], height=config["height"],
                          position=(config["x"], config["y"], config["z"]), color=(1, 1, 1, 1))


@dataclass(frozen=False)
class BallObject(Object):
    radius: float
    friction: float

    def to_config(self):
        config = {
            "type": "sphere",
            "x": self.position[0],
            "y": self.position[1],
            "z": self.position[2]
        }
        config["radius"] = self.radius
        return config

    @staticmethod
    def from_config(name, config):
        return BallObject(name=name, radius=config["radius"], position=(config["x"], config["y"], config["z"]),
                          color=(1, 1, 1, 1))
