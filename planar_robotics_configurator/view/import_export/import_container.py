import hydra_zen
from kivy.metrics import dp
from kivymd.uix.boxlayout import MDBoxLayout
from kivymd.uix.button import MDFlatButton
from kivymd.uix.widget import MDWidget
from plyer import filechooser

from planar_robotics_configurator.model.algorithm.algorithm_configuration import AlgorithmConfiguration
from planar_robotics_configurator.model.configurator_model import ConfiguratorModel
from planar_robotics_configurator.model.environment import Environment
from planar_robotics_configurator.view.utils import NonEmptyTextField, CustomIconButton, CustomLabel, CustomCheckbox, \
    CustomSnackbar


class ImportContainer(MDBoxLayout):

    def __init__(self):
        super().__init__()
        self.size_hint_x = 1
        self.orientation = "vertical"
        self.adaptive_height = True
        self.spacing = dp(15)
        file_layout = MDBoxLayout(orientation="horizontal", adaptive_height=True, spacing=dp(20))
        self.file_name = NonEmptyTextField(hint_text="File", pos_hint={"center_y": 0.5}, required=True)
        file_layout.add_widget(self.file_name)
        file_layout.add_widget(CustomIconButton(icon="folder", pos_hint={"center_y": 0.5},
                                                tooltip_text="Select folder", on_release=self.open_file_selection))
        self.add_widget(file_layout)

        self.algo_checkbox = CustomCheckbox(active=True,
                                            on_release=lambda instance: self.on_check_algorithm(instance.active))
        self.add_widget(MDBoxLayout(
            CustomLabel(text="Import Algorithm Configuration", pos_hint={'center_y': 0.5}),
            MDWidget(),
            self.algo_checkbox,
            orientation="horizontal", size_hint_x=1, adaptive_height=True, spacing=dp(10)))
        self.algorithm_name = NonEmptyTextField(hint_text="Algorithm Configuration Name", pos_hint={"center_y": 0.5},
                                                required=True)
        self.add_widget(self.algorithm_name)

        self.env_checkbox = CustomCheckbox(active=True,
                                           on_release=lambda instance: self.on_check_environment(instance.active))
        self.add_widget(MDBoxLayout(
            CustomLabel(text="Import Environment Configuration", pos_hint={'center_y': 0.5}),
            MDWidget(),
            self.env_checkbox,
            orientation="horizontal", size_hint_x=1, adaptive_height=True, spacing=dp(10)))
        self.environment_name = NonEmptyTextField(hint_text="Environment Configuration Name",
                                                  pos_hint={"center_y": 0.5}, required=True)
        self.add_widget(self.environment_name)

        self.add_widget(MDFlatButton(text="Import", pos_hint={'center_x': 0.5}, size_hint=(0.5, None),
                                     theme_text_color="Custom", text_color=(0, 0, 0, 1), md_bg_color=(1, 1, 1, 1),
                                     on_release=lambda _: self.on_import()))

    def reset(self):
        self.file_name.text = ""
        self.algorithm_name.text = ""
        self.on_check_algorithm(True)
        self.environment_name.text = ""
        self.on_check_environment(True)

    def check_fields(self) -> bool:
        if self.file_name.is_empty():
            CustomSnackbar(text="Please select a file to import")
            return False
        if self.algorithm_name.is_empty():
            CustomSnackbar(text="Please insert a algorithm name").open()
            return False
        if self.algo_checkbox.active and len(list(filter(lambda algo: algo.name == self.algorithm_name.text,
                                                         ConfiguratorModel().algorithm_configurations))) > 0:
            CustomSnackbar(text="Algorithm name is already used").open()
            return False
        if self.environment_name.is_empty():
            CustomSnackbar(text="Please insert a environment name").open()
            return False
        if self.env_checkbox.active and len(list(filter(lambda env: env.name == self.environment_name.text,
                                                        ConfiguratorModel().environments))) > 0:
            CustomSnackbar(text="Environment name is already used").open()
            return False
        return True

    def on_import(self):
        if not self.check_fields():
            return
        config = hydra_zen.load_from_yaml(self.file_name.text)
        if self.algo_checkbox.active:
            algorithms = list(filter(lambda algo: algo.name == config["algo"]["algo_name"], ConfiguratorModel().algorithms))
            if len(algorithms)==0:
                CustomSnackbar(text=f'No matching algorithm with name {config["algo"]["algo_name"]} found').open()
                return
            ConfiguratorModel().algorithm_configurations.append(
                AlgorithmConfiguration.from_config(self.algorithm_name.text, algorithms[0], config["algo"]))
        if self.env_checkbox.active:
            ConfiguratorModel().environments.append(Environment.from_config(self.environment_name.text, config["env"]))
        CustomSnackbar("Successfully imported").open()

    def open_file_selection(self, *args):
        res = filechooser.open_file(title="Select file", filters=["*.yaml"])
        if res is None or len(res) == 0:
            return
        self.file_name.text = res[0]

    def on_check_algorithm(self, value):
        self.algorithm_name.required = value
        self.algorithm_name.disabled = not value

    def on_check_environment(self, value):
        self.environment_name.required = value
        self.environment_name.disabled = not value
