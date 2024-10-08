from kivymd.uix.boxlayout import MDBoxLayout
from kivymd.uix.button import MDFlatButton
from kivymd.uix.dialog import MDDialog

from planar_robotics_configurator.model.configurator_model import ConfiguratorModel
from planar_robotics_configurator.model.algorithm.algorithm_configuration import AlgorithmConfiguration
from planar_robotics_configurator.view.utils import NonEmptyTextField, CustomSnackbar


class DialogContent(MDBoxLayout):

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.adaptive_height = True
        self.sim_name = NonEmptyTextField(hint_text="Name", required=True)
        self.add_widget(self.sim_name)


class AlgorithmConfigurationSettingsDialog(MDDialog):

    def __init__(self, algo_config_component, configuration: AlgorithmConfiguration = None):
        self.algo_config_component = algo_config_component
        self.configuration = configuration
        self.dialog_content = DialogContent()
        self.title = "Algorithm Configuration Settings" if self.configuration is not None else \
            "Algorithm Configuration Creation"
        super().__init__(type="custom",
                         content_cls=self.dialog_content,
                         buttons=[
                             MDFlatButton(
                                 text="Cancel",
                                 on_release=lambda *args: self.cancel()
                             ),
                             MDFlatButton(
                                 text="Add" if self.configuration is None else "Edit",
                                 theme_text_color="Custom",
                                 text_color=(0, 0, 0, 1),
                                 md_bg_color=(1, 1, 1, 1),
                                 on_release=lambda *args: self.confirm()
                             )
                         ])
        if self.configuration is not None:
            self.dialog_content.sim_name.text = self.configuration.name
        self.update_height()

    def cancel(self):
        self.dismiss()

    def check_name(self) -> bool:
        sim_names = list(map((lambda sim: sim.name),
                             filter((lambda sim: sim != self.configuration), ConfiguratorModel().algorithm_configurations)))
        return self.dialog_content.sim_name.text not in sim_names

    def confirm(self):
        if self.dialog_content.sim_name.is_empty():
            CustomSnackbar(text="Please fill out all fields").open()
            return
        if not self.check_name():
            CustomSnackbar(text="This name is already used").open()
            return
        if self.configuration is None:
            self.configuration = AlgorithmConfiguration(self.dialog_content.sim_name.text)
            ConfiguratorModel().algorithm_configurations.append(self.configuration)
        else:
            self.configuration.name = self.dialog_content.sim_name.text
        self.algo_config_component.set_configuration(self.configuration)
        self.dismiss()
