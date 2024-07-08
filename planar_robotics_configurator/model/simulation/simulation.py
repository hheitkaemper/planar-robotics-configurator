from dataclasses import dataclass, field

from planar_robotics_configurator.model.simulation.algorithm import Algorithm
from planar_robotics_configurator.model.simulation.parameter import ParameterValue


@dataclass(frozen=False)
class Simulation:
    """
    Represent a configuration of a training simulation.
    """
    name: str
    algorithm: Algorithm = None
    parameters: list[ParameterValue] = field(default_factory=list)

    def __post_init__(self):
        self.load_algorithm_parameters()

    def set_algorithm(self, algorithm: Algorithm):
        self.algorithm = algorithm
        self.load_algorithm_parameters()

    def load_algorithm_parameters(self):
        if self.algorithm is None:
            return
        self.parameters.clear()
        for parameter in self.algorithm.parameters:
            self.parameters.append(ParameterValue(parameter))
