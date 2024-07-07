from dataclasses import dataclass
from typing import Tuple


@dataclass(frozen=False)
class Object:
    name: str
    position: Tuple[float, float, float]
    color: Tuple[float, float, float, float]


@dataclass(frozen=False)
class RefObject(Object):
    fileRef: str


@dataclass(frozen=False)
class CubeObject(Object):
    width: float
    length: float
    height: float


@dataclass(frozen=False)
class BallObject(Object):
    radius: float
