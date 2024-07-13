from kivy.metrics import dp
from kivymd.uix.boxlayout import MDBoxLayout
from kivymd.uix.dropdownitem import MDDropDownItem
from kivymd.uix.floatlayout import MDFloatLayout
from kivymd.uix.label import MDLabel
from kivymd.uix.menu import MDDropdownMenu
from kivymd.uix.scrollview import MDScrollView
from kivymd.uix.widget import MDWidget

from planar_robotics_configurator.model.algorithm.parameter import ParameterValue, TypeParameter, BooleanParameter, \
    SelectionParameter
from planar_robotics_configurator.model.algorithm.algorithm_configuration import AlgorithmConfiguration
from planar_robotics_configurator.view.utils import CustomLabel, NonEmptyTextField, CustomIconButton, CustomCheckbox, \
    Divider


class AlgorithmParameter(MDBoxLayout):

    def __init__(self, parameter: ParameterValue):
        super(AlgorithmParameter, self).__init__()
        self.parameter = parameter
        self.orientation = "vertical"
        self.size_hint_x = 1
        self.adaptive_height = True
        self.md_bg_color = "#2F2F2F"
        self.padding = [dp(10), 0, dp(10), 0]

        layout = MDBoxLayout(orientation="horizontal", size_hint_x=1, adaptive_height=True, spacing=dp(10))
        layout.add_widget(CustomLabel(text=parameter.parameter.name, pos_hint={'center_y': 0.5}))
        layout.add_widget(MDWidget())
        if isinstance(parameter.parameter, TypeParameter):
            field = NonEmptyTextField(text=parameter.value, size_hint_x=None, width=dp(400), pos_hint={'center_y': 0.5},
                                      input_filter=parameter.parameter.type)
            field.bind(text=self.on_text_change)
            layout.add_widget(field)
        if isinstance(parameter.parameter, BooleanParameter):
            layout.padding = [0, dp(10), 0, dp(10)]
            checkbox = CustomCheckbox(pos_hint={'center_y': 0.5}, active=parameter.value == "True")
            checkbox.bind(active=self.on_checkbox_change)
            layout.add_widget(checkbox)
        if isinstance(parameter.parameter, SelectionParameter):
            layout.padding = [0, dp(10), 0, dp(10)]
            dropdown_item = MDDropDownItem(pos_hint={'center_y': 0.5})
            if parameter.value is None:
                dropdown_item.set_item("None")
            else:
                dropdown_item.set_item(parameter.value)
            dropdown_menu = MDDropdownMenu(position='bottom', caller=dropdown_item)
            dropdown_item.bind(on_release=lambda *args: dropdown_menu.open())
            for v in parameter.parameter.possible_values:
                dropdown_menu.items.append({
                    "text": v,
                    "on_release": lambda val=v: self.on_menu_selection(dropdown_menu, dropdown_item, val)
                })
            layout.add_widget(dropdown_item)
        expand_button = CustomIconButton(icon="chevron-down", pos_hint={'center_y': 0.5})
        expand_button.ripple_scale = 0
        expand_button.bind(on_release=self.on_expand)
        self.expand_button = expand_button
        layout.add_widget(expand_button)
        self.add_widget(layout)
        desc_layout = MDBoxLayout(orientation="vertical", size_hint_x=1, adaptive_height=True, spacing=dp(10),
                                  padding=[0, 0, 0, dp(10)])
        desc_layout.add_widget(Divider(orientation="horizontal", width=dp(2), md_bg_color=(1, 1, 1, 1)))
        desc_layout.add_widget(CustomLabel(text="Description", pos_hint={'center_y': 0.5}))
        label = MDLabel(text=self.parameter.parameter.description)
        label.adaptive_height = True
        label.bind(texture_size=lambda *x: label.setter("height")(
            label, label.texture_size[1]
        ))
        desc_layout.add_widget(label)
        self.desc_layout = desc_layout
        self.show_desc = False

    def on_text_change(self, instance, value):
        self.parameter.value = value

    def on_checkbox_change(self, instance, value):
        self.parameter.value = str(value)

    def on_menu_selection(self, menu, item, value):
        self.parameter.value = value
        item.set_item(value)
        menu.dismiss()

    def on_expand(self, *args):
        self.show_desc = not self.show_desc
        if self.show_desc:
            self.add_widget(self.desc_layout)
            self.expand_button.icon = "chevron-up"
        else:
            self.remove_widget(self.desc_layout)
            self.expand_button.icon = "chevron-down"


class SimulationParametersContainer(MDBoxLayout):

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.adaptive_height = True
        self.spacing = dp(10)
        self.padding = [dp(20), dp(20), 0, dp(20)]
        self.orientation = "vertical"


class SimulationParameters(MDFloatLayout):

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.size_hint = 0.8, 1
        self.container = SimulationParametersContainer()
        self.add_widget(MDScrollView(self.container, size_hint=(1, 1), pos_hint={'x': 0, 'y': 0}))

    def set_simulation(self, simulation: AlgorithmConfiguration):
        self.container.clear_widgets()
        for parameter in simulation.parameters:
            self.container.add_widget(AlgorithmParameter(parameter))
