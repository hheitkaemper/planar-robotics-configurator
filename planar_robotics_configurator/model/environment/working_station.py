from dataclasses import dataclass
from typing import Tuple


@dataclass(frozen=False)
class WorkingStation:
    name: str
    fileRef: str
    position: Tuple[float, float, float]
    color: Tuple[float, float, float, float]
