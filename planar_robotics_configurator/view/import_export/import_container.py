import hydra_zen
from kivy.metrics import dp
from kivymd.uix.boxlayout import MDBoxLayout
from kivymd.uix.button import MDFlatButton
from kivymd.uix.textfield import MDTextField
from kivymd.uix.widget import MDWidget
from omegaconf.errors import ConfigKeyError
from plyer import filechooser

from planar_robotics_configurator.model.algorithm.algorithm_configuration import AlgorithmConfiguration
from planar_robotics_configurator.model.configurator_model import ConfiguratorModel
from planar_robotics_configurator.model.environment import Environment
from planar_robotics_configurator.view.utils import NonEmptyTextField, CustomIconButton, CustomLabel, CustomCheckbox, \
    CustomSnackbar


class AlgorithmNotFoundException(Exception):

    def __init__(self, name, *args):
        self.name = name
        super().__init__(*args)


class ImportContainer(MDBoxLayout):
    """
    Layout for importing algorithm configurations and environment.
    It is possible to enable or disable the kinds of imports.
    """

    def __init__(self):
        super().__init__()
        self.size_hint_x = 1
        self.orientation = "vertical"
        self.adaptive_height = True
        self.spacing = dp(15)

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

        algo_file_layout = MDBoxLayout(orientation="horizontal", adaptive_height=True, spacing=dp(20))
        self.algo_file_name = NonEmptyTextField(hint_text="File", pos_hint={"center_y": 0.5}, required=True)
        algo_file_layout.add_widget(self.algo_file_name)
        self.algo_file_selection_button = CustomIconButton(icon="folder", pos_hint={"center_y": 0.5},
                                                           tooltip_text="Select file",
                                                           on_release=lambda _: self.open_file_selection(
                                                               self.algo_file_name))
        algo_file_layout.add_widget(self.algo_file_selection_button)
        self.add_widget(algo_file_layout)

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

        env_file_layout = MDBoxLayout(orientation="horizontal", adaptive_height=True, spacing=dp(20))
        self.env_file_name = NonEmptyTextField(hint_text="File", pos_hint={"center_y": 0.5}, required=True)
        env_file_layout.add_widget(self.env_file_name)
        self.env_file_selection_button = CustomIconButton(icon="folder", pos_hint={"center_y": 0.5},
                                                          tooltip_text="Select file",
                                                          on_release=lambda _: self.open_file_selection(
                                                              self.env_file_name))
        env_file_layout.add_widget(self.env_file_selection_button)
        self.add_widget(env_file_layout)

        self.add_widget(MDFlatButton(text="Import", pos_hint={'center_x': 0.5}, size_hint=(0.5, None),
                                     theme_text_color="Custom", text_color=(0, 0, 0, 1), md_bg_color=(1, 1, 1, 1),
                                     on_release=lambda _: self.on_import()))

    def check_fields(self) -> bool:
        """
        Checks all input field values to make sure they are valid/fulfilled.
        """
        if self.algo_checkbox.active:
            if self.algorithm_name.is_empty():
                CustomSnackbar(text="Please insert a algorithm name").open()
                return False
            if len(list(filter(lambda algo: algo.name == self.algorithm_name.text,
                               ConfiguratorModel().algorithm_configurations))) > 0:
                CustomSnackbar(text="Algorithm name is already used").open()
                return False
            if self.algo_file_name.is_empty():
                CustomSnackbar(text="Please select a algorithm configuration file to import")
                return False

        if self.env_checkbox.active:
            if self.environment_name.is_empty():
                CustomSnackbar(text="Please insert a environment name").open()
                return False
            if len(list(filter(lambda env: env.name == self.environment_name.text,
                               ConfiguratorModel().environments))) > 0:
                CustomSnackbar(text="Environment name is already used").open()
                return False
            if self.env_file_name.is_empty():
                CustomSnackbar(text="Please select a environment configuration file to import")
                return False
        return True

    def on_import(self):
        """
        On clicking import.
        Checks the fields and tries to import the algorithm configuration and environment.
        """
        if not self.check_fields():
            return
        info = {"algo": None, "env": None}
        if self.algo_checkbox.active:
            file_name = self.algo_file_name.text
            try:
                config = hydra_zen.load_from_yaml(file_name)
                algo_config = config["algo"]
                algo_name = algo_config["algo_name"]
                algorithms = list(
                    filter(lambda algo: algo.name == algo_name, ConfiguratorModel().algorithms))
                if len(algorithms) == 0:
                    raise AlgorithmNotFoundException(name=algo_name)
                ConfiguratorModel().algorithm_configurations.append(
                    AlgorithmConfiguration.from_config(self.algorithm_name.text, algorithms[0], algo_config))
                info["algo"] = "Successfully imported algorithm configuration."
            except FileNotFoundError:
                info["algo"] = f"Failed importing algorithm configuration. File with name {file_name} not found."
            except ConfigKeyError as e:
                info["algo"] = (f"Failed importing algorithm configuration. "
                                f"Config not containing key {e.full_key}.")
            except AlgorithmNotFoundException as e:
                info["algo"] = (f"Failed importing algorithm configuration. "
                                f"Algorithm with name {e.name} not found.")
        else:
            info["algo"] = "Algorithm configuration import disabled."
        if self.env_checkbox.active:
            file_name = self.env_file_name.text
            try:
                config = hydra_zen.load_from_yaml(file_name)
                ConfiguratorModel().environments.append(
                    Environment.from_config(self.environment_name.text, config["env"]))
                info["env"] = "Successfully imported environment configuration."
            except FileNotFoundError:
                info["env"] = "Failed importing environment. File with name {file_name} not found."
            except ConfigKeyError as e:
                info["env"] = (f"Failed importing environment. "
                               f"Config not containing key {e.full_key}.")
        else:
            info["env"] = "Environment import disabled."
        CustomSnackbar(f"{info['algo']}\n{info['env']}").open()

    def open_file_selection(self, field: MDTextField):
        """
        Opens a file chooser and stores the selected file in the given field.
        :param field: MDTextField instance of which the text should be changed.
        """
        res = filechooser.open_file(title="Select file", filters=["*.yaml"])
        if res is None or len(res) == 0:
            return
        field.text = res[0]

    def on_check_algorithm(self, value):
        """
        On switching the state of the checkbox for activating the algorithm configuration import.
        Enables/disables all inputs for the algorithm configuration.
        """
        self.algo_file_selection_button.disabled = not value
        self.algorithm_name.required_copy = value
        self.algorithm_name.on_focus(self.algorithm_name, False)
        self.algorithm_name.disabled = not value
        self.algo_file_name.required_copy = value
        self.algo_file_name.on_focus(self.algo_file_name, False)
        self.algo_file_name.disabled = not value

    def on_check_environment(self, value):
        """
        On switching the state of the checkbox for activating the environment import.
        Enables/disables all inputs for the environment.
        """
        self.env_file_selection_button.disabled = not value
        self.environment_name.required_copy = value
        self.environment_name.on_focus(self.environment_name, False)
        self.environment_name.disabled = not value
        self.env_file_name.required_copy = value
        self.env_file_name.on_focus(self.env_file_name, False)
        self.env_file_name.disabled = not value
