from kivymd.uix.floatlayout import MDFloatLayout

from planar_robotics_configurator.model.simulation.algorithm import Algorithm
from planar_robotics_configurator.model.simulation.simulation import Simulation
from planar_robotics_configurator.view.simulation.algorithm_information import SimulationAlgorithmInformation
from planar_robotics_configurator.view.simulation.simulation_selection import SimulationSelection


class SimulationSideInformation(MDFloatLayout):

    def __init__(self, sim_component):
        super(SimulationSideInformation, self).__init__()
        self.sim_component = sim_component
        self.size_hint = 0.2, 1
        self.pos_hint = {'x': 0.8}
        self.selection = SimulationSelection(self.sim_component)
        self.add_widget(self.selection)
        self.algorithm_info = SimulationAlgorithmInformation(self.sim_component)
        self.add_widget(self.algorithm_info)

    def set_simulation(self, simulation: Simulation):
        self.selection.set_text(simulation.name)
        self.set_algorithm(simulation.algorithm)

    def set_algorithm(self, algorithm: Algorithm):
        self.algorithm_info.set_algorithm(algorithm)
