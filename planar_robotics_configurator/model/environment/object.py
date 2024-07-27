from dataclasses import dataclass
from typing import Tuple


@dataclass(frozen=False)
class Object:
    name: str
    position: Tuple[float, float, float]
    color: Tuple[float, float, float, float]

    def to_config(self):
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


@dataclass(frozen=False)
class CubeObject(Object):
    width: float
    length: float
    height: float

    def to_config(self):
        config = {
            "type": "cube",
            "x": self.position[0],
            "y": self.position[1],
            "z": self.position[2]
        }
        config["width"] = self.width
        config["length"] = self.length
        config["height"] = self.height
        return config


@dataclass(frozen=False)
class BallObject(Object):
    radius: float

    def to_config(self):
        config = {
            "type": "ball",
            "x": self.position[0],
            "y": self.position[1],
            "z": self.position[2]
        }
        config["radius"] = self.radius
        return config
