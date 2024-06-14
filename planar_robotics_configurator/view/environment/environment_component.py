from kivy.metrics import dp
from kivymd.uix.anchorlayout import MDAnchorLayout
from kivymd.uix.button import MDIconButton
from kivymd.uix.floatlayout import MDFloatLayout
from kivymd.uix.gridlayout import MDGridLayout
from kivymd.uix.menu import MDDropdownMenu

from planar_robotics_configurator.model.configurator_model import ConfiguratorModel
from planar_robotics_configurator.model.environment.environment import Environment
from planar_robotics_configurator.view.environment.environment_map import EnvironmentMap
from planar_robotics_configurator.view.utils import CustomLabel, AdaptiveDropDownItem


class EnvironmentSelection(MDAnchorLayout):
    """
    Defines an overlay for selecting the environment in the right top corner.
    This layout provides a dropdown menu for selecting an environment with all environments saved in the model.
    """

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.anchor_x = "right"
        self.anchor_y = "top"
        self.padding = [dp(0), dp(10), dp(10), dp(0)]
        create_button = MDIconButton(icon="plus", theme_text_color="Custom", text_color=(1, 1, 1, 1))
        create_button._default_icon_pad /= 4
        self.dropdown_item = AdaptiveDropDownItem(adaptive_width=True)
        self.dropdown_item.set_item(
            ConfiguratorModel().environments[0].name if len(ConfiguratorModel().environments) > 0 else "None")
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

    def select_item(self, environment: Environment):
        self.dropdown_item.set_item(environment.name)
        self.parent.set_environment(environment)
        self.dropdown_menu.dismiss()


class EnvironmentComponent(MDFloatLayout):
    """
    The layout for the environment site.
    """

    def __init__(self):
        super().__init__()
        self.size_hint = 1, 1
        self.environment: Environment | None = ConfiguratorModel().environments[0] if len(
            ConfiguratorModel().environments) > 0 else None
        self.map = EnvironmentMap(self.environment)
        self.add_widget(self.map)
        self.add_widget(EnvironmentSelection())

    def set_environment(self, environment: Environment):
        self.environment = environment
        self.map.set_environment(environment)
