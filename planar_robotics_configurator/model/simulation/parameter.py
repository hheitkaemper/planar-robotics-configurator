from dataclasses import dataclass, field


@dataclass(frozen=False)
class Parameter:
    """
    Abstract Parameter. Every parameter should have a name and a description.
    :param name: Name of the parameter.
    :param description: Description of the parameter.
    """
    name: str
    description: str


@dataclass(frozen=False)
class ParameterValue:
    """
    Represents an instance of a parameter, which has a value.
    Sets the value to the default value if no value is specified.
    """
    parameter: Parameter
    value: str = None

    def __post_init__(self):
        if self.value is not None:
            return
        if isinstance(self.parameter, BooleanParameter):
            self.value = str(True)
        if isinstance(self.parameter, TypeParameter):
            self.value = self.parameter.default


@dataclass(frozen=False)
class SelectionParameter(Parameter):
    """
    Parameter which can be one of the possible values.
    :param possible_values: specifies the possible values.
    """
    possible_values: list[str]


@dataclass(frozen=False)
class BooleanParameter(Parameter):
    """
    Parameter which can be true or false.
    """
    pass


@dataclass(frozen=False)
class TypeParameter(Parameter):
    """
    Parameter with a given type. The type can be None, 'int', 'float'. It is possible to specify a default value.
    :param type: type of the parameter: None, 'int', 'float'
    :param default: default value. Should be of the specified type.
    """
    type: str
    default: str


@dataclass(frozen=False)
class ConfigParameter:
    """
    Represents a parameter in the config. Should only be used for config.
    """
    name: str
    description: str
    parameter_type: str
    possible_values: list[str] = field(default_factory=list)
    type: str = ""
    default: str = ""

    @staticmethod
    def to_parameter(self) -> Parameter:
        match self.parameter_type:
            case 'BooleanParameter':
                return BooleanParameter(self.name, self.description)
            case 'TypeParameter':
                return TypeParameter(self.name, self.description, self.type, self.default)
            case 'SelectionParameter':
                return SelectionParameter(self.name, self.description, self.possible_values)
        raise ValueError(f'Parameter type {self.parameter_type} not supported')
