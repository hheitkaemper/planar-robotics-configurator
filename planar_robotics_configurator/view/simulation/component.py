from kivymd.uix.floatlayout import MDFloatLayout

from planar_robotics_configurator.model.configurator_model import ConfiguratorModel
from planar_robotics_configurator.model.simulation.algorithm import Algorithm
from planar_robotics_configurator.model.simulation.simulation import Simulation
from planar_robotics_configurator.view.simulation.parameters import SimulationParameters
from planar_robotics_configurator.view.simulation.side_information import SimulationSideInformation
from planar_robotics_configurator.view.utils import Component


class SimulationComponent(MDFloatLayout, Component):
    def __init__(self):
        super().__init__()
        self.size_hint = 1, 1
        self.simulation = None
        self.side_information = SimulationSideInformation(self)
        self.add_widget(self.side_information)
        self.parameters = SimulationParameters()
        self.add_widget(self.parameters)

    def on_select(self, _):
        if self.simulation is not None:
            return
        if len(ConfiguratorModel().simulations) == 0:
            return
        self.simulation = ConfiguratorModel().simulations[0]
        self.set_simulation(self.simulation)

    def set_simulation(self, simulation: Simulation):
        self.simulation = simulation
        self.side_information.set_simulation(self.simulation)
        self.parameters.set_simulation(self.simulation)

    def set_algorithm(self, algorithm: Algorithm):
        self.side_information.set_algorithm(algorithm)
