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


class ParameterLayout(MDBoxLayout):
    def __init__(self, parameter_value: ParameterValue, **kwargs):
        self.parameter_value = parameter_value
        super().__init__(orientation="horizontal", size_hint_x=1, adaptive_height=True, spacing=dp(10))
        self.add_widget(CustomLabel(text=parameter_value.parameter.name, pos_hint={'center_y': 0.5}))


class TypeParameterLayout(ParameterLayout):
    def __init__(self, parameter_value: ParameterValue, **kwargs):
        super().__init__(parameter_value=parameter_value, kwargs=kwargs)
        self.add_widget(CustomLabel(text=f'[{parameter_value.parameter.type}]', pos_hint={'center_y': 0.5}))
        self.add_widget(MDWidget())
        field = NonEmptyTextField(text=parameter_value.value, size_hint_x=None, width=dp(400),
                                  pos_hint={'center_y': 0.5}, input_filter=parameter_value.parameter.type)
        field.bind(text=self.on_text_change)
        self.add_widget(field)

    def on_text_change(self, instance, value):
        self.parameter_value.value = value


class BooleanParameterLayout(ParameterLayout):
    def __init__(self, parameter_value: ParameterValue, **kwargs):
        super().__init__(parameter_value=parameter_value, kwargs=kwargs)
        self.add_widget(MDWidget())
        self.padding = [0, dp(10), 0, dp(10)]
        checkbox = CustomCheckbox(pos_hint={'center_y': 0.5}, active=parameter_value.value == "True")
        checkbox.bind(active=self.on_checkbox_change)
        self.add_widget(checkbox)

    def on_checkbox_change(self, instance, value):
        self.parameter_value.value = str(value)


class SelectionParameterLayout(ParameterLayout):

    def __init__(self, parameter_value: ParameterValue, **kwargs):
        super().__init__(parameter_value=parameter_value, kwargs=kwargs)
        self.add_widget(MDWidget())
        self.padding = [0, dp(10), 0, dp(10)]
        dropdown_item = MDDropDownItem(pos_hint={'center_y': 0.5})
        if parameter_value.value is None:
            dropdown_item.set_item("None")
        else:
            dropdown_item.set_item(parameter_value.value)
        dropdown_menu = MDDropdownMenu(position='bottom', caller=dropdown_item)
        dropdown_item.bind(on_release=lambda *args: dropdown_menu.open())
        for v in parameter_value.parameter.possible_values:
            dropdown_menu.items.append({
                "text": v,
                "on_release": lambda val=v: self.on_menu_selection(dropdown_menu, dropdown_item, val)
            })
        self.add_widget(dropdown_item)

    def on_menu_selection(self, menu, item, value):
        self.parameter_value.value = value
        item.set_item(value)
        menu.dismiss()


class AlgorithmConfigurationParameter(MDBoxLayout):
    def __init__(self, parameter_value: ParameterValue):
        super(AlgorithmConfigurationParameter, self).__init__()
        self.parameter_value = parameter_value
        self.orientation = "vertical"
        self.size_hint_x = 1
        self.adaptive_height = True
        self.md_bg_color = "#2F2F2F"
        self.padding = [dp(10), 0, dp(10), 0]
        if isinstance(parameter_value.parameter, TypeParameter):
            layout = TypeParameterLayout(parameter_value=parameter_value)
        elif isinstance(parameter_value.parameter, SelectionParameter):
            layout = SelectionParameterLayout(parameter_value=parameter_value)
        elif isinstance(parameter_value.parameter, BooleanParameter):
            layout = BooleanParameterLayout(parameter_value=parameter_value)
        else:
            raise ValueError(f'Parameter type not supported')
        expand_button = CustomIconButton(icon="chevron-down", pos_hint={'center_y': 0.5}, ripple_scale=0,
                                         on_release=self.on_expand)
        self.expand_button = expand_button
        layout.add_widget(expand_button)
        self.add_widget(layout)
        desc_layout = MDBoxLayout(orientation="vertical", size_hint_x=1, adaptive_height=True, spacing=dp(10),
                                  padding=[0, 0, 0, dp(10)])
        desc_layout.add_widget(Divider(orientation="horizontal", width=dp(2), md_bg_color=(1, 1, 1, 1)))
        desc_layout.add_widget(CustomLabel(text="Description", pos_hint={'center_y': 0.5}))
        label = MDLabel(text=parameter_value.parameter.description, adaptive_height=True)
        label.bind(texture_size=lambda *x: label.setter("height")(
            label, label.texture_size[1]
        ))
        desc_layout.add_widget(label)
        self.desc_layout = desc_layout
        self.show_desc = False

    def on_expand(self, *args):
        self.show_desc = not self.show_desc
        if self.show_desc:
            self.add_widget(self.desc_layout)
            self.expand_button.icon = "chevron-up"
        else:
            self.remove_widget(self.desc_layout)
            self.expand_button.icon = "chevron-down"


class AlgorithmConfigurationParametersContainer(MDBoxLayout):

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.adaptive_height = True
        self.spacing = dp(10)
        self.padding = [dp(20), dp(20), 0, dp(20)]
        self.orientation = "vertical"


class AlgorithmConfigurationParameters(MDFloatLayout):

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.size_hint = 0.8, 1
        self.container = AlgorithmConfigurationParametersContainer()
        self.add_widget(MDScrollView(self.container, size_hint=(1, 1), pos_hint={'x': 0, 'y': 0}))

    def set_configuration(self, configuration: AlgorithmConfiguration):
        self.container.clear_widgets()
        if configuration is None:
            return
        for parameter in configuration.parameters:
            self.container.add_widget(AlgorithmConfigurationParameter(parameter))
