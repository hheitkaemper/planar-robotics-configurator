from kivy.metrics import dp
from kivymd.uix.anchorlayout import MDAnchorLayout
from kivymd.uix.boxlayout import MDBoxLayout
from kivymd.uix.button import MDFlatButton
from kivymd.uix.dialog import MDDialog
from kivymd.uix.menu import MDDropdownMenu

from planar_robotics_configurator.model.configurator_model import ConfiguratorModel
from planar_robotics_configurator.model.algorithm.algorithm_configuration import AlgorithmConfiguration
from planar_robotics_configurator.view.algorithm.dialog import AlgorithmConfigurationSettingsDialog
from planar_robotics_configurator.view.utils import AdaptiveDropDownItem, CustomLabel, CustomIconButton, CustomSnackbar


class AlgorithmConfigurationSelection(MDAnchorLayout):

    def __init__(self, algo_config_component, **kwargs):
        super().__init__(**kwargs)
        self.algo_config_component = algo_config_component
        self.anchor_x = "left"
        self.anchor_y = "top"
        self.pos_hint = {"x": 0}
        self.padding = [dp(10), dp(10), dp(10), dp(10)]
        create_button = CustomIconButton(icon="plus",
                                         tooltip_text="Create algorithm configuration",
                                         on_release=lambda *x: AlgorithmConfigurationSettingsDialog(
                                             self.algo_config_component).open())
        delete_button = CustomIconButton(icon="trash-can-outline",
                                         tooltip_text="Delete algorithm configuration",
                                         on_release=lambda *x: self.open_delete())
        settings_button = CustomIconButton(icon="cog-outline",
                                           tooltip_text="Edit algorithm configuration",
                                           on_release=lambda *x: self.open_settings())
        self.dropdown_item = AdaptiveDropDownItem(size_hint_x=1)
        self.set_text("None")
        self.dropdown_item.on_release = self.open_menu
        self.dropdown_menu = MDDropdownMenu(position='bottom', caller=self.dropdown_item)
        self.add_widget(MDBoxLayout(
            CustomLabel(text="Current configuration", padding=[dp(4), dp(0), dp(8), dp(8)]),
            self.dropdown_item,
            MDBoxLayout(create_button, delete_button, settings_button, orientation="horizontal",
                        adaptive_height=True),
            orientation='vertical',
            adaptive_height=True),
        )

    def open_delete(self):
        if self.algo_config_component.configuration is None:
            CustomSnackbar(text="Please select an configuration first!").open()
            return
        delete_dialog = MDDialog(title="Are you sure you want to delete this configuration?", buttons=[
            MDFlatButton(
                text="Cancel",
                on_release=lambda instance: instance.parent.parent.parent.parent.dismiss()
            ),
            MDFlatButton(
                text="Delete",
                theme_text_color="Custom",
                text_color=(0, 0, 0, 1),
                md_bg_color=(1, 1, 1, 1),
                on_release=lambda instance: self.on_delete(instance.parent.parent.parent.parent)
            )
        ])
        delete_dialog.open()

    def on_delete(self, dialog):
        ConfiguratorModel().algorithm_configurations.remove(self.algo_config_component.configuration)
        if len(ConfiguratorModel().algorithm_configurations) == 0:
            self.algo_config_component.set_configuration(None)
        else:
            self.algo_config_component.set_configuration(ConfiguratorModel().algorithm_configurations[0])
        dialog.dismiss()

    def open_settings(self):
        if self.algo_config_component.configuration is None:
            CustomSnackbar(text="Please select an configuration first!").open()
            return
        AlgorithmConfigurationSettingsDialog(self.algo_config_component,
                                             self.algo_config_component.configuration).open()

    def open_menu(self):
        self.dropdown_menu.items = []
        for simulation in ConfiguratorModel().algorithm_configurations:
            self.dropdown_menu.items.append({
                "text": simulation.name,
                "on_release": lambda x=simulation: self.select_item(x)
            })
        self.dropdown_menu.open()

    def set_text(self, text):
        self.dropdown_item.set_item(text)

    def select_item(self, simulation: AlgorithmConfiguration):
        self.set_text(simulation.name)
        self.algo_config_component.set_configuration(simulation)
        self.dropdown_menu.dismiss()
