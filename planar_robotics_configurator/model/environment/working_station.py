from dataclasses import dataclass
from typing import Tuple


@dataclass(frozen=False)
class WorkingStation:
    name: str
    fileRef: str
    position: Tuple[float, float, float]
    color: Tuple[float, float, float, float]

    def to_config(self):
        config = {
            "ref": self.fileRef,
            "x": self.position[0],
            "y": self.position[1],
            "z": self.position[2]
        }
        return config
