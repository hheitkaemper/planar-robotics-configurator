from dataclasses import dataclass, field

from planar_robotics_configurator.model.algorithm.algorithm import Algorithm
from planar_robotics_configurator.model.algorithm.parameter import (TypeParameter, BooleanParameter,
                                                                    SelectionParameter, SelectionParameterValue,
                                                                    TypeParameterValue, BooleanParameterValue)


@dataclass(frozen=False)
class AlgorithmConfiguration:
    """
    Represent a configuration of a training algorithm.
    """
    name: str
    algorithm: Algorithm = None
    parameters: list = field(default_factory=list)

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
            if isinstance(parameter, SelectionParameter):
                self.parameters.append(SelectionParameterValue(name=parameter.name,
                                                               description=parameter.description,
                                                               default=parameter.default,
                                                               possible_values=parameter.possible_values))
            if isinstance(parameter, TypeParameter):
                self.parameters.append(TypeParameterValue(name=parameter.name,
                                                          description=parameter.description,
                                                          default=parameter.default,
                                                          type=parameter.type))
            if isinstance(parameter, BooleanParameter):
                self.parameters.append(BooleanParameterValue(name=parameter.name,
                                                             description=parameter.description,
                                                             default=parameter.default))

    def to_config(self):
        config = {}
        config['algo_name'] = self.algorithm.name
        for parameter in self.parameters:
            parameter.to_config(config, "")
        return config

    @staticmethod
    def from_config(name, algorithm, config):
        algorithm_configuration = AlgorithmConfiguration(name=name,
                                                         algorithm=algorithm)
        for parameter in algorithm_configuration.parameters:
            parameter.from_config(config, "")
        return algorithm_configuration
