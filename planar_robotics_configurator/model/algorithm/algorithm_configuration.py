from dataclasses import dataclass, field

from planar_robotics_configurator.model.algorithm.algorithm import Algorithm
from planar_robotics_configurator.model.algorithm.parameter import ParameterValue, TypeParameter, BooleanParameter, \
    SelectionParameter


@dataclass(frozen=False)
class AlgorithmConfiguration:
    """
    Represent a configuration of a training algorithm.
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

    def to_config(self):
        config = {}
        config['algo_name'] = self.algorithm.name
        for parameter in self.parameters:
            if isinstance(parameter.parameter, SelectionParameter):
                config[parameter.parameter.name] = parameter.value
            elif isinstance(parameter.parameter, BooleanParameter):
                config[parameter.parameter.name] = parameter.value == "True"
            elif isinstance(parameter.parameter, TypeParameter):
                type = parameter.parameter.type
                if type == "int":
                    config[parameter.parameter.name] = int(parameter.value) if parameter.value != '' else 0
                    continue
                if type == "float":
                    config[parameter.parameter.name] = float(parameter.value) if parameter.value != '' else 0
                    continue
                config[parameter.parameter.name] = parameter.value
        return config

    @staticmethod
    def from_config(name, algorithm, config):
        algorithm_configuration = AlgorithmConfiguration(name=name,
                                                         algorithm=algorithm)
        for parameter in algorithm_configuration.parameters:
            parameter.value = str(config[parameter.parameter.name])
        return algorithm_configuration
