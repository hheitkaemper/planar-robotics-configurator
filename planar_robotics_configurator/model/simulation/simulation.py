from dataclasses import dataclass, field

from planar_robotics_configurator.model.simulation.parameter import ParameterValue


@dataclass(frozen=False)
class Simulation:
    name: str
    parameters: list[ParameterValue] = field(default_factory=list)
