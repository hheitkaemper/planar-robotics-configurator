from planar_robotics_configurator.model.environment.environment import Environment


class ConfiguratorModel:
    """
    Model of the configurator which stores all information about the environments and simulations parameters.
    Singleton class which is only possible to instantiate once.
    Thus, it can be used at any position at the view and always has every information.
    """
    instance = None

    def __init__(self):
        if self.__class__.instance is not None:
            return
        self.__class__.instance = self
        self.environments: list[Environment] = []

    def __new__(cls, *args, **kwargs):
        if not cls.instance:
            return super(ConfiguratorModel, cls).__new__(cls)
        return cls.instance
