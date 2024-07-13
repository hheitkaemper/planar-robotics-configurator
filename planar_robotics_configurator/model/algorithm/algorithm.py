from dataclasses import dataclass, field

from planar_robotics_configurator.model.algorithm.parameter import Parameter, ConfigParameter


@dataclass(frozen=False)
class Algorithm:
    name: str
    description: str
    parameters: list[Parameter] = field(default_factory=list)


@dataclass(frozen=False)
class ConfigAlgorithm:
    name: str
    description: str
    parameters: list[ConfigParameter] = field(default_factory=list)

    @staticmethod
    def to_algorithm(self) -> Algorithm:
        parameters = []
        for parameter in self.parameters:
            parameters.append(ConfigParameter.to_parameter(parameter))
        return Algorithm(name=self.name, description=self.description, parameters=parameters)
