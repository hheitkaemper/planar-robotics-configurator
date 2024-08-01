import os

from hydra_zen import to_yaml
from kivy.metrics import dp
from kivymd.uix.boxlayout import MDBoxLayout
from kivymd.uix.button import MDFlatButton
from kivymd.uix.dropdownitem import MDDropDownItem
from kivymd.uix.menu import MDDropdownMenu
from kivymd.uix.textfield import MDTextField
from kivymd.uix.widget import MDWidget
from plyer import filechooser

from planar_robotics_configurator.model.configurator_model import ConfiguratorModel
from planar_robotics_configurator.view.utils import CustomIconButton, NonEmptyTextField, CustomLabel, CustomSnackbar


class ExportContainer(MDBoxLayout):
    """
    Layout for exporting algorithm configurations and environments.
    """

    def __init__(self):
        super().__init__()
        self.size_hint_x = 1
        self.orientation = "vertical"
        self.adaptive_height = True
        self.spacing = dp(15)
        self.selected_algo_config = None
        self.selected_env = None

        self.algo_dropdown_item = MDDropDownItem(pos_hint={'center_y': 0.5})
        self.algo_dropdown_item.set_item("None")
        algo_dropdown_menu = MDDropdownMenu(position='bottom', caller=self.algo_dropdown_item)
        self.algo_dropdown_item.bind(
            on_release=lambda *args: self.open_algorithm_dropdown_menu(algo_dropdown_menu, self.algo_dropdown_item))
        self.add_widget(MDBoxLayout(
            CustomLabel(text="Algorithm Configuration", pos_hint={'center_y': 0.5}),
            MDWidget(),
            self.algo_dropdown_item,
            orientation="horizontal", size_hint_x=1, adaptive_height=True, spacing=dp(10)))

        algo_file_layout = MDBoxLayout(orientation="horizontal", adaptive_height=True, spacing=dp(20))
        self.algo_file_name = NonEmptyTextField(hint_text="Algorithm Configuration File", pos_hint={"center_y": 0.5},
                                                required=True)
        algo_file_layout.add_widget(self.algo_file_name)
        self.algo_file_selection_button = CustomIconButton(icon="folder", pos_hint={"center_y": 0.5},
                                                           tooltip_text="Select file",
                                                           on_release=lambda _: self.open_file_selection(
                                                               self.algo_file_name))
        algo_file_layout.add_widget(self.algo_file_selection_button)
        self.add_widget(algo_file_layout)

        self.env_dropdown_item = MDDropDownItem(pos_hint={'center_y': 0.5})
        self.env_dropdown_item.set_item("None")
        env_dropdown_menu = MDDropdownMenu(position='bottom', caller=self.env_dropdown_item)
        self.env_dropdown_item.bind(
            on_release=lambda *args: self.open_environment_dropdown_menu(env_dropdown_menu, self.env_dropdown_item))
        self.add_widget(MDBoxLayout(
            CustomLabel(text="Environment Configuration", pos_hint={'center_y': 0.5}),
            MDWidget(),
            self.env_dropdown_item,
            orientation="horizontal", size_hint_x=1, adaptive_height=True, spacing=dp(10)))

        env_file_layout = MDBoxLayout(orientation="horizontal", adaptive_height=True, spacing=dp(20))
        self.env_file_name = NonEmptyTextField(hint_text="Environment Configuration File", pos_hint={"center_y": 0.5},
                                               required=True)
        env_file_layout.add_widget(self.env_file_name)
        self.env_file_selection_button = CustomIconButton(icon="folder", pos_hint={"center_y": 0.5},
                                                          tooltip_text="Select file",
                                                          on_release=lambda _: self.open_file_selection(
                                                              self.env_file_name))
        env_file_layout.add_widget(self.env_file_selection_button)
        self.add_widget(env_file_layout)

        self.add_widget(MDFlatButton(text="Export", pos_hint={'center_x': 0.5}, size_hint=(0.5, None),
                                     theme_text_color="Custom", text_color=(0, 0, 0, 1), md_bg_color=(1, 1, 1, 1),
                                     on_release=lambda _: self.on_export()))

    def check_fields(self):
        """
        Checks if the fields are fulfilled.
        """
        if self.selected_algo_config is not None and self.algo_file_name.is_empty():
            CustomSnackbar(text="Please select path for algorithm configuration").open()
            return False
        if self.selected_env is not None and self.env_file_name.is_empty():
            CustomSnackbar(text="Please select path for environment configuration").open()
            return False
        return True

    def on_export(self):
        """
        Called when the export button is clicked.
        Exports the selected algorithm configuration and environment.
        """
        if not self.check_fields():
            return
        info = {"algo": None, "env": None}
        if self.selected_algo_config is not None:
            config = {
                "algo": self.selected_algo_config.to_config()
            }
            path = self.algo_file_name.text
            if os.path.exists(path):
                os.remove(path)
            with open(path, "w") as f:
                f.write(to_yaml(config))
            info["algo"] = "Successfully exported algorithm configuration."
        else:
            info["algo"] = "Algorithm configuration export disabled."
        if self.selected_env is not None:
            config = {
                "env": self.selected_env.to_config()
            }
            path = self.env_file_name.text
            if os.path.exists(path):
                os.remove(path)
            with open(path, "w") as f:
                f.write(to_yaml(config))
            info["env"] = "Successfully exported environment."
        else:
            info["env"] = "Environment export disabled."
        CustomSnackbar(text=f"{info['algo']}\n{info['env']}").open()

    def open_algorithm_dropdown_menu(self, menu, item):
        """
        Opens a dropdown menu item with all available algorithms.
        Algorithm configurations where the algorithm is not selected are not available.
        """
        menu.items = []
        algo_configs = ConfiguratorModel().algorithm_configurations
        menu.items.append({
            "text": "None",
            "on_release": lambda *args: self.on_algorithm_select(menu, item, None)
        })
        for algoConfig in algo_configs:
            if algoConfig.algorithm is None:
                continue
            menu.items.append({
                "text": algoConfig.name,
                "on_release": lambda val=algoConfig: self.on_algorithm_select(menu, item, val)
            })
        menu.open()

    def on_algorithm_select(self, menu, item, algo_config):
        """
        Called when the user selects an algorithm in the dropdown menu.
        Disables/Enables the fields for the algorithm configuration export.
        """
        if algo_config is None:
            self.enable_algorithm_fields(False)
            item.set_item("None")
        else:
            self.enable_algorithm_fields(True)
            item.set_item(algo_config.name)
        self.selected_algo_config = algo_config
        menu.dismiss()

    def open_environment_dropdown_menu(self, menu, item):
        """
        Opens a dropdown menu item with all available environments.
        """
        menu.items = []
        environments = ConfiguratorModel().environments
        menu.items.append({
            "text": "None",
            "on_release": lambda *args: self.on_environment_select(menu, item, None)
        })
        for env in environments:
            menu.items.append({
                "text": env.name,
                "on_release": lambda val=env: self.on_environment_select(menu, item, val)
            })
        menu.open()

    def on_environment_select(self, menu, item, env):
        """
        Called when the user selects an environment in the dropdown menu.
        Disables/Enables the fields for the algorithm configuration export.
        """
        if env is None:
            self.enable_environment_fields(False)
            item.set_item("None")
        else:
            self.enable_environment_fields(True)
            item.set_item(env.name)
        self.selected_env = env
        menu.dismiss()

    def open_file_selection(self, field: MDTextField):
        """
        Opens a file chooser.
        Sets the selected file as text of the field.
        :param field: Field of which the text should be the file path.
        """
        res = filechooser.save_file(title="Select file", filters=["*.yaml"])
        if res is None or len(res) == 0:
            return
        field.text = res[0] if res[0].endswith(".yaml") else res[0] + ".yaml"

    def reset(self):
        """
        Resets the export to avoid deleted configurations to be listed.
        """
        self.selected_algo_config = None
        self.enable_algorithm_fields(False)
        self.selected_env = None
        self.enable_environment_fields(False)
        self.algo_dropdown_item.set_item("None")
        self.env_dropdown_item.set_item("None")

    def enable_algorithm_fields(self, enabled: bool) -> None:
        """
        Enables the fields for the algorithm configuration export.
        """
        self.algo_file_name.required_copy = enabled
        self.algo_file_name.on_focus(self.algo_file_name, False)
        self.algo_file_name.disabled = not enabled
        self.algo_file_selection_button.disabled = not enabled

    def enable_environment_fields(self, enabled: bool) -> None:
        """
        Enables the fields for the environment configuration export.
        """
        self.env_file_name.required_copy = enabled
        self.env_file_name.on_focus(self.env_file_name, False)
        self.env_file_name.disabled = not enabled
        self.env_file_selection_button.disabled = not enabled
