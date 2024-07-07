from dataclasses import dataclass, field


@dataclass(frozen=False)
class Parameter:
    name: str
    description: str


@dataclass(frozen=False)
class ParameterValue:
    parameter: Parameter
    value: str


@dataclass(frozen=False)
class SelectionParameter(Parameter):
    possible_values: list[str]


@dataclass(frozen=False)
class BooleanParameter(Parameter):
    pass


@dataclass(frozen=False)
class TypeParameter(Parameter):
    type: str
    default: str


@dataclass(frozen=False)
class ConfigParameter:
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
