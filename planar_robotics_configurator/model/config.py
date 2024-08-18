from dataclasses import dataclass
from typing import Mapping, List

from planar_robotics_configurator.model.algorithm.algorithm import ConfigAlgorithm
from planar_robotics_configurator.model.environment import MoverPreset


@dataclass(frozen=False)
class Config:
    algorithms: Mapping[str, ConfigAlgorithm]
    mover_presets: List[MoverPreset]
