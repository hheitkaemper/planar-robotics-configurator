from kivymd.uix.floatlayout import MDFloatLayout

from planar_robotics_configurator.model.configurator_model import ConfiguratorModel
from planar_robotics_configurator.model.algorithm.algorithm import Algorithm
from planar_robotics_configurator.model.algorithm.algorithm_configuration import AlgorithmConfiguration
from planar_robotics_configurator.view.algorithm.parameters import AlgorithmConfigurationParameters
from planar_robotics_configurator.view.algorithm.side_information import SimulationSideInformation
from planar_robotics_configurator.view.utils import Component


class AlgorithmConfigurationComponent(MDFloatLayout, Component):
    def __init__(self):
        super().__init__()
        self.size_hint = 1, 1
        self.configuration = None
        self.side_information = SimulationSideInformation(self)
        self.add_widget(self.side_information)
        self.parameters = AlgorithmConfigurationParameters()
        self.add_widget(self.parameters)

    def on_select(self, _):
        if self.configuration is not None:
            return
        if len(ConfiguratorModel().algorithm_configurations) == 0:
            return
        self.configuration = ConfiguratorModel().algorithm_configurations[0]
        self.set_configuration(self.configuration)

    def set_configuration(self, simulation: AlgorithmConfiguration):
        self.configuration = simulation
        self.side_information.set_configuration(self.configuration)
        self.parameters.set_configuration(self.configuration)

    def set_algorithm(self, algorithm: Algorithm):
        self.side_information.set_algorithm(algorithm)
