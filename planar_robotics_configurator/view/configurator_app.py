from kivy.clock import Clock
from kivy.uix.widget import Widget
from kivymd.app import MDApp
from kivymd.uix.gridlayout import MDGridLayout
from kivymd.uix.screen import MDScreen

from planar_robotics_configurator.view.environment.component import EnvironmentComponent
from planar_robotics_configurator.view.navigation_component import NavigationComponent
from planar_robotics_configurator.view.algorithm.component import AlgorithmConfigurationComponent
from planar_robotics_configurator.view.utils import Component


class ConfiguratorApp(MDApp):

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.layout = None
        self.view = None

    def build(self):
        screen = MDScreen()
        screen.theme_cls.theme_style = "Dark"
        screen.md_bg_color = "373737"
        self.layout = MDGridLayout(cols=1, orientation='lr-bt')
        nav = NavigationComponent(self)
        sim = AlgorithmConfigurationComponent()
        nav.add_tab("Algorithm", sim)
        nav.add_tab("Environment", EnvironmentComponent())
        self.layout.add_widget(nav)
        self.set_view(sim)
        screen.add_widget(self.layout)
        return screen

    def set_view(self, widget: (Component, Widget)):
        if self.view is not None:
            self.layout.remove_widget(self.view)
        self.view = widget
        self.layout.add_widget(self.view, 1)
        Clock.schedule_once(widget.on_select)
