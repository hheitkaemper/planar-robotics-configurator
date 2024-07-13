from kivymd.uix.floatlayout import MDFloatLayout

from planar_robotics_configurator.model.algorithm.algorithm import Algorithm
from planar_robotics_configurator.model.algorithm.algorithm_configuration import AlgorithmConfiguration
from planar_robotics_configurator.view.algorithm.algorithm_information import AlgorithmInformation
from planar_robotics_configurator.view.algorithm.configuration_selection import AlgorithmConfigurationSelection


class SimulationSideInformation(MDFloatLayout):

    def __init__(self, sim_component):
        super(SimulationSideInformation, self).__init__()
        self.sim_component = sim_component
        self.size_hint = 0.2, 1
        self.pos_hint = {'x': 0.8}
        self.selection = AlgorithmConfigurationSelection(self.sim_component)
        self.add_widget(self.selection)
        self.algorithm_info = AlgorithmInformation(self.sim_component)
        self.add_widget(self.algorithm_info)

    def set_simulation(self, simulation: AlgorithmConfiguration):
        self.selection.set_text(simulation.name)
        self.set_algorithm(simulation.algorithm)

    def set_algorithm(self, algorithm: Algorithm):
        self.algorithm_info.set_algorithm(algorithm)
