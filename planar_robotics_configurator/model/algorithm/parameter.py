from dataclasses import dataclass, field


@dataclass(frozen=False)
class Parameter:
    """
    Abstract Parameter. Every parameter should have a name and a description.
    :param name: Name of the parameter.
    :param description: Description of the parameter.
    """
    name: str = None
    description: str = None
    default: str = None


@dataclass(frozen=False)
class Value:
    """
    Abstract Value object. Every parameter value should have a value.
    Defines abstract methods for import and export.
    :param value: Value of the parameter.
    """
    value: any = None

    def to_config(self, config, prefix):
        raise NotImplementedError()

    def from_config(self, config, prefix):
        raise NotImplementedError()


@dataclass(frozen=False)
class BooleanParameter(Parameter):
    """
    Parameter which can be true or false.
    """
    pass


@dataclass(frozen=False)
class BooleanParameterValue(BooleanParameter, Value):
    """
    Boolean Parameter with value.
    """

    def __post_init__(self):
        if self.default is None:
            return
        self.value = bool(self.default)

    def to_config(self, config, prefix):
        config[prefix + self.name] = self.value

    def from_config(self, config, prefix):
        self.value = config[prefix + self.name]


@dataclass(frozen=False)
class TypeParameter(Parameter):
    """
    Parameter with a given type. The type can be None, 'int', 'float'. It is possible to specify a default value.
    :param type: type of the parameter: None, 'int', 'float'
    :param default: default value. Should be of the specified type.
    """
    type: str = None


@dataclass(frozen=False)
class TypeParameterValue(TypeParameter, Value):
    """
    TypeParameter with value.
    """

    def __post_init__(self):
        if self.default is None:
            return
        self.value = self.default

    def to_config(self, config, prefix):
        if self.type == "int":
            v: int = int(self.value) if self.value != '' else int(0)
            config[prefix + self.name] = v
            return
        if self.type == "float":
            v: float = float(self.value) if self.value != '' else float(0)
            config[prefix + self.name] = v
            return
        config[prefix + self.name] = self.value

    def from_config(self, config, prefix):
        self.value = str(config[prefix + self.name])


@dataclass(frozen=False)
class SelectionParameter(Parameter):
    """
    Parameter which can be one of the possible values.
    :param possible_values: specifies the possible values.
    """
    possible_values: dict[str, list[Parameter]] = field(default_factory=dict)


@dataclass(frozen=False)
class SelectionParameterValue(SelectionParameter, Value):
    """
    SelectionParameter with value and a list of the values contained by the parameter list of the possible values.
    """
    values: list = field(default_factory=list)

    def __post_init__(self):
        if self.default is None:
            return
        self.value = self.default
        self.update_parameters()

    def update_parameters(self):
        self.values = []
        for parameter in self.possible_values[self.value]:
            if isinstance(parameter, SelectionParameter):
                self.values.append(SelectionParameterValue(name=parameter.name,
                                                           description=parameter.description,
                                                           default=parameter.default,
                                                           possible_values=parameter.possible_values))
            if isinstance(parameter, TypeParameter):
                self.values.append(TypeParameterValue(name=parameter.name,
                                                      description=parameter.description,
                                                      default=parameter.default,
                                                      type=parameter.type))
            if isinstance(parameter, BooleanParameter):
                self.values.append(BooleanParameterValue(name=parameter.name,
                                                         description=parameter.description,
                                                         default=parameter.default))

    def to_config(self, config, prefix):
        config[prefix + self.name] = self.value
        for parameter_value in self.values:
            parameter_value.to_config(config, prefix + self.name + ".")

    def from_config(self, config, prefix):
        self.value = config[prefix + self.name]
        for parameter_value in self.values:
            parameter_value.from_config(config, prefix + self.name + ".")


@dataclass(frozen=False)
class ConfigParameter:
    """
    Represents a parameter in the config. Should only be used for config.
    """
    name: str
    description: str
    parameter_type: str
    possible_values: any
    type: str = ""
    default: str = ""

    @staticmethod
    def to_parameter(self) -> Parameter:
        match self.parameter_type:
            case 'BooleanParameter':
                return BooleanParameter(self.name, self.description, self.default)
            case 'TypeParameter':
                return TypeParameter(self.name, self.description, self.default, self.type)
            case 'SelectionParameter':
                possible_values = {}
                for val in self.possible_values:
                    parameters = []
                    for param in val.parameters:
                        parameters.append(ConfigParameter.to_parameter(param))
                    possible_values[val.name] = parameters
                return SelectionParameter(self.name, self.description, self.default, possible_values)
        raise ValueError(f'Parameter type {self.parameter_type} not supported')
