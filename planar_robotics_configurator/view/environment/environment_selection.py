from kivy.metrics import dp
from kivymd.uix.anchorlayout import MDAnchorLayout
from kivymd.uix.gridlayout import MDGridLayout
from kivymd.uix.menu import MDDropdownMenu

from planar_robotics_configurator.model.configurator_model import ConfiguratorModel
from planar_robotics_configurator.model.environment.environment import Environment
from planar_robotics_configurator.view.environment.dialog import EnvironmentSettingsDialog
from planar_robotics_configurator.view.utils import AdaptiveDropDownItem, CustomLabel, CustomIconButton


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
        self.add_widget(MDGridLayout(
            CustomLabel(text="Current configuration", padding=[dp(4), dp(0), dp(8), dp(8)]),
            MDGridLayout(self.dropdown_item, create_button, rows=1, adaptive_width=True),
            cols=1, size_hint=(None, None), adaptive_width=True)
        )

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
