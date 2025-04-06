from dataclasses import dataclass, field
from sys import prefix
from typing import List, Union

from planar_robotics_configurator.model.environment.parameter import ConfigParameter, FloatParameter, IntParameter, BooleanParameter, Parameter


@dataclass(frozen=False)
class ParameterGroup:
    """
    Parameter group containing all additional parameters with values.
    """
    name: str
    prefix: str
    parameters: List[Union[FloatParameter, IntParameter, BooleanParameter]] = field(default_factory=list)

    def copy_group(self):
        """
        Create a copy of this ParameterGroup. Containing a copy of each parameter.
        """
        parameters = []
        for parameter in self.parameters:
            if isinstance(parameter, FloatParameter):
                parameters.append(FloatParameter(parameter.name, parameter.code, parameter.type, parameter.hint, parameter.default, parameter.value))
            elif isinstance(parameter, IntParameter):
                parameters.append(IntParameter(parameter.name, parameter.code, parameter.type, parameter.hint, parameter.default, parameter.value))
            elif isinstance(parameter, BooleanParameter):
                parameters.append(BooleanParameter(parameter.name, parameter.code, parameter.type, parameter.hint, parameter.default, parameter.value))
            else:
                raise ValueError(f"Not supported type {type(parameter)}")
        return ParameterGroup(self.name, self.prefix, parameters)

@dataclass(frozen=False)
class ParameterGroupConfiguration:
    """
    Parameter group configuration containing all additional parameters without values.
    """

    name: str
    prefix: str
    parameters: List[Parameter] = field(default_factory=list)

    def to_parameter_group(self):
        parameters = []
        for parameter in self.parameters:
            parameters.append(parameter.to_parameter())
        return ParameterGroup(name=self.name, prefix=self.prefix, parameters=parameters)

@dataclass(frozen=False)
class ConfigParameterGroup:
    """
    Config class which is used to parse the config. Should not be used for anything else.
    """
    name: str
    prefix: str
    parameters: List[ConfigParameter] = field(default_factory=list)

    @staticmethod
    def to_parameter_group_configuration(self) -> ParameterGroupConfiguration:
        parameters = []
        for parameter in self.parameters:
            parameters.append(ConfigParameter.to_parameter(parameter))
        return ParameterGroupConfiguration(name=self.name, prefix=self.prefix, parameters=parameters)