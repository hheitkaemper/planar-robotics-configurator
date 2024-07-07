from dataclasses import dataclass
from typing import Mapping

from planar_robotics_configurator.model.simulation.algorithm import ConfigAlgorithm


@dataclass(frozen=False)
class Config:
    algorithms: Mapping[str, ConfigAlgorithm]
