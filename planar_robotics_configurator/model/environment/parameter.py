from dataclasses import dataclass

from omegaconf.errors import ConfigKeyError


@dataclass(frozen=False)
class Parameter:
    """
    Abstract Parameter
    """
    name: str = None
    code: str= None
    type: str = None
    hint: str = None
    default: str = None

    def to_parameter(self):
        match self.type:
            case "float":
                return FloatParameter(self.name, self.code, self.type, self.hint, self.default)
            case "int":
                return IntParameter(self.name, self.code, self.type, self.hint, self.default)
            case "boolean":
                return BooleanParameter(self.name, self.code, self.type, self.hint, self.default)
        raise ValueError(f'Env Parameter type {self.type} not supported')

    def to_config(self, prefix, config):
        raise NotImplementedError()

    def from_config(self, prefix, config):
        raise NotImplementedError()

    def get_config_name(self, prefix) -> str:
        name = ""
        if prefix is not None and prefix != '':
            name += prefix
            name += "."
        name += self.code
        return name

@dataclass(frozen=False)
class FloatParameter(Parameter):
    """
    Parameter with float value
    """
    value: float = None

    def __post_init__(self):
        if self.default is None:
            return
        if self.value is not None:
            return
        self.value = float(self.default)

    def to_config(self, prefix, config):
        config[self.get_config_name(prefix)] = self.value if self.value is not None else float(
            self.default)

    def from_config(self, prefix, config):
        try:
            self.value = float(config[self.get_config_name(prefix)])
        except ConfigKeyError as e:
            if self.default is None:
                return
            self.value = float(self.default)


@dataclass(frozen=False)
class IntParameter(Parameter):
    """
    Parameter with int value
    """
    value: int = None

    def __post_init__(self):
        if self.default is None:
            return
        if self.value is not None:
            return
        self.value = int(self.default)

    def to_config(self, prefix, config):
        config[self.get_config_name(prefix)] = self.value if self.value is not None else int(
            self.default)

    def from_config(self, prefix, config):
        try:
            self.value = int(config[self.get_config_name(prefix)])
        except ConfigKeyError as e:
            if self.default is None:
                return
            self.value = int(self.default)

@dataclass(frozen=False)
class BooleanParameter(Parameter):
    """
    Parameter with boolean value
    """
    value: bool = None

    def __post_init__(self):
        if self.default is None:
            return
        if self.value is not None:
            return
        self.value = bool(self.default)

    def to_config(self, prefix, config):
        config[self.get_config_name(prefix)] = self.value if self.value is not None else bool(
            self.default)

    def from_config(self, prefix, config):
        try:
            self.value = bool(config[self.get_config_name(prefix)])
        except ConfigKeyError as e:
            if self.default is None:
                return
            self.value = bool(self.default)

@dataclass(frozen=False)
class ConfigParameter:
    """
    Represents a parameter in the config. Should only be used for config.
    """
    name: str
    code: str
    hint: str
    type: str
    default: str

    @staticmethod
    def to_parameter(self) -> Parameter:
        return Parameter(self.name, self.code, self.type, self.hint, self.default)
