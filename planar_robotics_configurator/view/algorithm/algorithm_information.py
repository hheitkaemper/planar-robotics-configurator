from kivy.metrics import dp
from kivymd.uix.boxlayout import MDBoxLayout
from kivymd.uix.label import MDLabel
from kivymd.uix.menu import MDDropdownMenu

from planar_robotics_configurator.model.configurator_model import ConfiguratorModel
from planar_robotics_configurator.model.algorithm.algorithm import Algorithm
from planar_robotics_configurator.view.utils import CustomLabel, AdaptiveDropDownItem, CustomSnackbar


class AlgorithmInformation(MDBoxLayout):

    def __init__(self, algo_config_component):
        super(AlgorithmInformation, self).__init__()
        self.algo_config_component = algo_config_component
        self.orientation = "vertical"
        self.pos_hint = {'x': 0, 'top': 0.8}
        self.size_hint_x = 1
        self.adaptive_height = True
        self.padding = [dp(10), dp(10), dp(10), dp(10)]
        self.spacing = dp(20)

        self.dropdown_item = AdaptiveDropDownItem(size_hint_x=1)
        self.set_text("None")
        self.dropdown_item.on_release = self.open_menu
        self.dropdown_menu = MDDropdownMenu(position='bottom', caller=self.dropdown_item)
        self.add_widget(MDBoxLayout(
            CustomLabel(text="Current algorithm", padding=[dp(4), dp(0), dp(8), dp(8)]),
            self.dropdown_item,
            orientation='vertical',
            adaptive_height=True))

        label = MDLabel(
            text="desc")
        self.desc_label = label
        label.adaptive_height = True
        label.bind(texture_size=lambda *x: label.setter("height")(
            label, label.texture_size[1]
        ))
        self.desc_layout = MDBoxLayout(CustomLabel(text="Description"), label, spacing=dp(10), adaptive_height=True,
                                       orientation="vertical", md_bg_color="#2F2F2F",
                                       padding=[dp(10), dp(10), dp(10), dp(10)])
        self.show_desc = False

    def open_menu(self):
        if self.algo_config_component.configuration is None:
            CustomSnackbar(text="Please select an configuration first!").open()
            return
        self.dropdown_menu.items = []
        for algorithm in ConfiguratorModel().algorithms:
            self.dropdown_menu.items.append({
                "text": algorithm.name,
                "on_release": lambda x=algorithm: self.select_item(x)
            })
        self.dropdown_menu.open()

    def set_text(self, text):
        self.dropdown_item.set_item(text)

    def set_algorithm(self, algorithm: Algorithm):
        if algorithm is None:
            if self.show_desc:
                self.remove_widget(self.desc_layout)
            self.set_text("None")
            return
        self.set_text(algorithm.name)
        self.desc_label.text = algorithm.description
        if not self.show_desc:
            self.add_widget(self.desc_layout)
            self.show_desc = True

    def select_item(self, algorithm: Algorithm):
        if self.algo_config_component.configuration is not None:
            self.algo_config_component.configuration.set_algorithm(algorithm)
        self.algo_config_component.set_configuration(self.algo_config_component.configuration)
        self.dropdown_menu.dismiss()
