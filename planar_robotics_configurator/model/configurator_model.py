from planar_robotics_configurator.model.config import Config
from planar_robotics_configurator.model.environment.environment import Environment
from planar_robotics_configurator.model.environment.mover_preset import MoverPreset
from planar_robotics_configurator.model.algorithm.algorithm import Algorithm, ConfigAlgorithm
from planar_robotics_configurator.model.algorithm.algorithm_configuration import AlgorithmConfiguration


class ConfiguratorModel:
    """
    Model of the configurator which stores all information about the environments and algorithm_configurations parameters.
    Singleton class which is only possible to instantiate once.
    Thus, it can be used at any position at the view and always has every information.
    """
    instance = None

    def __init__(self):
        if self.__class__.instance is not None:
            return
        self.__class__.instance = self
        self.environments: list[Environment] = []
        self.mover_presets: list[MoverPreset] = []
        self.algorithms: list[Algorithm] = []
        self.algorithm_configurations: list[AlgorithmConfiguration] = []

    def __new__(cls, *args, **kwargs):
        if not cls.instance:
            return super(ConfiguratorModel, cls).__new__(cls)
        return cls.instance

    def load_config(self, config: Config):
        for algorithm in config.algorithms.values():
            self.algorithms.append(ConfigAlgorithm.to_algorithm(algorithm))
