from kivy.metrics import dp
from kivymd.uix.anchorlayout import MDAnchorLayout
from kivymd.uix.boxlayout import MDBoxLayout
from kivymd.uix.menu import MDDropdownMenu

from planar_robotics_configurator.model.configurator_model import ConfiguratorModel
from planar_robotics_configurator.model.simulation.simulation import Simulation
from planar_robotics_configurator.view.simulation.dialog import SimulationSettingsDialog
from planar_robotics_configurator.view.utils import AdaptiveDropDownItem, CustomLabel, CustomIconButton, CustomSnackbar


class SimulationSelection(MDAnchorLayout):

    def __init__(self, sim_component, **kwargs):
        super().__init__(**kwargs)
        self.sim_component = sim_component
        self.anchor_x = "left"
        self.anchor_y = "top"
        self.pos_hint = {"x": 0}
        self.padding = [dp(10), dp(10), dp(10), dp(10)]
        create_button = CustomIconButton(icon="plus",
                                         tooltip_text="Create simulation",
                                         on_release=lambda *x: SimulationSettingsDialog(self.sim_component).open())
        settings_button = CustomIconButton(icon="cog-outline",
                                           tooltip_text="Edit simulation",
                                           on_release=lambda *x: self.open_settings())
        self.dropdown_item = AdaptiveDropDownItem(size_hint_x=1)
        self.set_text("None")
        self.dropdown_item.on_release = self.open_menu
        self.dropdown_menu = MDDropdownMenu(position='bottom', caller=self.dropdown_item)
        self.add_widget(MDBoxLayout(
            CustomLabel(text="Current configuration", padding=[dp(4), dp(0), dp(8), dp(8)]),
            MDBoxLayout(self.dropdown_item, create_button, settings_button, orientation="horizontal",
                        adaptive_height=True),
            orientation='vertical',
            adaptive_height=True))

    def open_settings(self):
        if self.sim_component.simulation is None:
            CustomSnackbar(text="Please select an simulation first!").open()
            return
        SimulationSettingsDialog(self.sim_component, self.sim_component.simulation).open()

    def open_menu(self):
        self.dropdown_menu.items = []
        for simulation in ConfiguratorModel().simulations:
            self.dropdown_menu.items.append({
                "text": simulation.name,
                "on_release": lambda x=simulation: self.select_item(x)
            })
        self.dropdown_menu.open()

    def set_text(self, text):
        self.dropdown_item.set_item(text)

    def select_item(self, simulation: Simulation):
        self.set_text(simulation.name)
        self.sim_component.set_simulation(simulation)
        self.dropdown_menu.dismiss()
