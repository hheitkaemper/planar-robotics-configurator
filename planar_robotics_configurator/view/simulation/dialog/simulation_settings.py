from kivymd.uix.boxlayout import MDBoxLayout
from kivymd.uix.button import MDFlatButton
from kivymd.uix.dialog import MDDialog

from planar_robotics_configurator.model.configurator_model import ConfiguratorModel
from planar_robotics_configurator.model.simulation.simulation import Simulation
from planar_robotics_configurator.view.utils import NonEmptyTextField, CustomSnackbar


class DialogContent(MDBoxLayout):

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.adaptive_height = True
        self.sim_name = NonEmptyTextField(hint_text="Simulation Name", required=True)
        self.add_widget(self.sim_name)


class SimulationSettingsDialog(MDDialog):

    def __init__(self, sim_component, simulation: Simulation = None):
        self.sim_component = sim_component
        self.simulation = simulation
        self.dialog_content = DialogContent()
        self.title = "Simulation Settings" if self.simulation is not None else "Simulation Creation"
        super().__init__(type="custom",
                         content_cls=self.dialog_content,
                         buttons=[
                             MDFlatButton(
                                 text="Cancel",
                                 on_release=lambda *args: self.cancel()
                             ),
                             MDFlatButton(
                                 text="Add" if self.simulation is None else "Edit",
                                 theme_text_color="Custom",
                                 text_color=(0, 0, 0, 1),
                                 md_bg_color=(1, 1, 1, 1),
                                 on_release=lambda *args: self.confirm()
                             )
                         ])
        if self.simulation is not None:
            self.dialog_content.sim_name.text = self.simulation.name
        self.update_height()

    def cancel(self):
        self.dismiss()

    def check_name(self) -> bool:
        sim_names = list(map((lambda sim: sim.name),
                             filter((lambda sim: sim != self.simulation), ConfiguratorModel().simulations)))
        return self.dialog_content.sim_name.text not in sim_names

    def confirm(self):
        if self.dialog_content.sim_name.is_empty():
            CustomSnackbar(text="Please fill out all fields").open()
            return
        if not self.check_name():
            CustomSnackbar(text="This name is already used").open()
            return
        if self.simulation is None:
            self.simulation = Simulation(self.dialog_content.sim_name.text)
            ConfiguratorModel().simulations.append(self.simulation)
        else:
            self.simulation.name = self.dialog_content.sim_name.text
        self.sim_component.set_simulation(self.simulation)
        self.dismiss()
