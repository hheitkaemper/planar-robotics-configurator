import os

from hydra_zen import to_yaml
from kivy.metrics import dp
from kivymd.uix.boxlayout import MDBoxLayout
from kivymd.uix.button import MDFlatButton
from kivymd.uix.dropdownitem import MDDropDownItem
from kivymd.uix.menu import MDDropdownMenu
from kivymd.uix.widget import MDWidget
from plyer import filechooser

from planar_robotics_configurator.model.configurator_model import ConfiguratorModel
from planar_robotics_configurator.view.utils import CustomIconButton, NonEmptyTextField, CustomLabel, CustomSnackbar


class ExportContainer(MDBoxLayout):

    def __init__(self):
        super().__init__()
        self.size_hint_x = 1
        self.orientation = "vertical"
        self.adaptive_height = True
        self.spacing = dp(15)
        self.selected_algo_config = None
        self.selected_env = None
        file_layout = MDBoxLayout(orientation="horizontal", adaptive_height=True, spacing=dp(20))
        self.file_name = NonEmptyTextField(hint_text="File", pos_hint={"center_y": 0.5}, required=True)
        file_layout.add_widget(self.file_name)
        file_layout.add_widget(CustomIconButton(icon="folder", pos_hint={"center_y": 0.5},
                                                tooltip_text="Select folder", on_release=self.open_file_selection))
        self.add_widget(file_layout)
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
        self.add_widget(MDFlatButton(text="Export", pos_hint={'center_x': 0.5}, size_hint=(0.5, None),
                                     theme_text_color="Custom", text_color=(0, 0, 0, 1), md_bg_color=(1, 1, 1, 1),
                                     on_release=lambda _: self.on_export()))

    def on_export(self):
        if self.selected_algo_config is None or self.selected_env is None:
            CustomSnackbar(text="Please select an algorithm configuration and an environment configuration").open()
            return
        if self.file_name.is_empty():
            CustomSnackbar(text="Please select a filepath for the export").open()
            return
        path = self.file_name.text
        if os.path.exists(path):
            os.remove(path)
        config = {}
        config["env"] = self.selected_env.to_config()
        config["algo"] = self.selected_algo_config.to_config()
        with open(path, "w") as f:
            f.write(to_yaml(config))
        CustomSnackbar(text="Successfully saved config").open()

    def open_algorithm_dropdown_menu(self, menu, item):
        menu.items = []
        algo_configs = ConfiguratorModel().algorithm_configurations
        if len(algo_configs) == 0:
            CustomSnackbar(text="No algorithm configuration found.").open()
            return
        for algoConfig in algo_configs:
            menu.items.append({
                "text": algoConfig.name,
                "on_release": lambda val=algoConfig: self.on_algorithm_select(menu, item, val)
            })
        menu.open()

    def on_algorithm_select(self, menu, item, algo_config):
        item.set_item(algo_config.name)
        self.selected_algo_config = algo_config
        menu.dismiss()

    def open_environment_dropdown_menu(self, menu, item):
        menu.items = []
        environments = ConfiguratorModel().environments
        if len(environments) == 0:
            CustomSnackbar(text="No environment configuration found.").open()
            return
        for env in environments:
            menu.items.append({
                "text": env.name,
                "on_release": lambda val=env: self.on_environment_select(menu, item, val)
            })
        menu.open()

    def on_environment_select(self, menu, item, env):
        item.set_item(env.name)
        self.selected_env = env
        menu.dismiss()

    def open_file_selection(self, *args):
        res = filechooser.save_file(title="Select file", filters=["*.yaml"])
        if res is None or len(res) == 0:
            return
        self.file_name.text = res[0]

    def reset(self):
        self.selected_algo_config = None
        self.selected_env = None
        self.file_name.text = ""
        self.algo_dropdown_item.set_item("None")
        self.env_dropdown_item.set_item("None")
