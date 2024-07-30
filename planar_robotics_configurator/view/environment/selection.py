from kivy.metrics import dp
from kivymd.uix.anchorlayout import MDAnchorLayout
from kivymd.uix.button import MDFlatButton
from kivymd.uix.dialog import MDDialog
from kivymd.uix.gridlayout import MDGridLayout
from kivymd.uix.menu import MDDropdownMenu

from planar_robotics_configurator.model.configurator_model import ConfiguratorModel
from planar_robotics_configurator.model.environment import Environment
from planar_robotics_configurator.view.environment.dialog import EnvironmentSettingsDialog
from planar_robotics_configurator.view.utils import AdaptiveDropDownItem, CustomLabel, CustomIconButton, CustomSnackbar


class EnvironmentSelection(MDAnchorLayout):
    """
    Defines an overlay for selecting the environment in the right top corner.
    This layout provides a dropdown menu for selecting an environment with all environments saved in the model.
    """

    def __init__(self, env_component, **kwargs):
        super().__init__(**kwargs)
        self.env_component = env_component
        self.anchor_x = "right"
        self.anchor_y = "top"
        self.padding = [dp(0), dp(10), dp(10), dp(0)]
        create_button = CustomIconButton(icon="plus",
                                         tooltip_text="Create environment",
                                         on_release=lambda *x: EnvironmentSettingsDialog(self.env_component).open())
        self.dropdown_item = AdaptiveDropDownItem(adaptive_width=True)
        self.set_text("None")
        self.dropdown_item.on_release = self.open_menu
        self.dropdown_menu = MDDropdownMenu(position='bottom', caller=self.dropdown_item)
        delete_button = CustomIconButton(icon="trash-can-outline",
                                         tooltip_text="Delete environment",
                                         on_release=lambda *x: self.open_delete())
        self.add_widget(MDGridLayout(
            CustomLabel(text="Current configuration", padding=[dp(4), dp(0), dp(8), dp(8)]),
            MDGridLayout(self.dropdown_item, create_button, delete_button, rows=1, adaptive_width=True),
            cols=1, size_hint=(None, None), adaptive_width=True)
        )

    def open_delete(self):
        if self.env_component.environment is None:
            CustomSnackbar(text="Please select an environment first!").open()
            return
        delete_dialog = MDDialog(title="Are you sure you want to delete this environment?", buttons=[
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
        ConfiguratorModel().environments.remove(self.env_component.environment)
        if len(ConfiguratorModel().environments) == 0:
            self.env_component.set_environment(None)
        else:
            self.env_component.set_environment(ConfiguratorModel().environments[0])
        dialog.dismiss()

    def open_menu(self):
        self.dropdown_menu.items = []
        for environment in ConfiguratorModel().environments:
            self.dropdown_menu.items.append({
                "text": environment.name,
                "on_release": lambda x=environment: self.select_item(x)
            })
        self.dropdown_menu.open()

    def set_text(self, text):
        self.dropdown_item.set_item(text)

    def select_item(self, environment: Environment):
        self.set_text(environment.name)
        self.env_component.set_environment(environment)
        self.dropdown_menu.dismiss()
