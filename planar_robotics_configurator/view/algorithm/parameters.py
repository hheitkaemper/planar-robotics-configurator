from kivy.metrics import dp
from kivymd.uix.boxlayout import MDBoxLayout
from kivymd.uix.dropdownitem import MDDropDownItem
from kivymd.uix.floatlayout import MDFloatLayout
from kivymd.uix.label import MDLabel
from kivymd.uix.menu import MDDropdownMenu
from kivymd.uix.scrollview import MDScrollView
from kivymd.uix.widget import MDWidget

from planar_robotics_configurator.model.algorithm.algorithm_configuration import AlgorithmConfiguration
from planar_robotics_configurator.model.algorithm.parameter import TypeParameterValue, BooleanParameterValue, \
    SelectionParameterValue
from planar_robotics_configurator.view.utils import CustomLabel, NonEmptyTextField, CustomIconButton, CustomCheckbox, \
    Divider


class ParameterLayout(MDBoxLayout):
    def __init__(self, parameter_value, **kwargs):
        self.parameter_value = parameter_value
        super().__init__(orientation="horizontal", size_hint_x=1, adaptive_height=True, spacing=dp(10))
        self.add_widget(CustomLabel(text=parameter_value.name, pos_hint={'center_y': 0.5}))


class TypeParameterLayout(ParameterLayout):
    def __init__(self, parameter_value: TypeParameterValue, **kwargs):
        super().__init__(parameter_value=parameter_value, kwargs=kwargs)
        if parameter_value.type is not None:
            self.add_widget(CustomLabel(text=f'[{parameter_value.type}]', pos_hint={'center_y': 0.5}))
        self.add_widget(MDWidget())
        field = NonEmptyTextField(text=parameter_value.value, size_hint_x=None, width=dp(400),
                                  pos_hint={'center_y': 0.5}, input_filter=parameter_value.type)
        field.bind(text=self.on_text_change)
        self.add_widget(field)

    def on_text_change(self, instance, value):
        self.parameter_value.value = value


class BooleanParameterLayout(ParameterLayout):
    def __init__(self, parameter_value: BooleanParameterValue, **kwargs):
        super().__init__(parameter_value=parameter_value, kwargs=kwargs)
        self.add_widget(MDWidget())
        self.padding = [0, dp(10), 0, dp(10)]
        checkbox = CustomCheckbox(pos_hint={'center_y': 0.5}, active=parameter_value.value)
        checkbox.bind(active=self.on_checkbox_change)
        self.add_widget(checkbox)

    def on_checkbox_change(self, instance, value):
        self.parameter_value.value = value


class SelectionParameterLayout(ParameterLayout):

    def __init__(self, parameter_value: SelectionParameterValue, callback, **kwargs):
        super().__init__(parameter_value=parameter_value, kwargs=kwargs)
        self.callback = callback
        self.add_widget(MDWidget())
        self.padding = [0, dp(10), 0, dp(10)]
        dropdown_item = MDDropDownItem(pos_hint={'center_y': 0.5})
        if parameter_value.value is None:
            dropdown_item.set_item("None")
        else:
            dropdown_item.set_item(parameter_value.value)
        dropdown_menu = MDDropdownMenu(position='bottom', caller=dropdown_item)
        dropdown_item.bind(on_release=lambda *args: dropdown_menu.open())
        for k in parameter_value.possible_values.keys():
            dropdown_menu.items.append({
                "text": k,
                "on_release": lambda val=k: self.on_menu_selection(dropdown_menu, dropdown_item, val)
            })
        self.add_widget(dropdown_item)

    def on_menu_selection(self, menu, item, value):
        self.parameter_value.value = value
        self.parameter_value.update_parameters()
        self.callback()
        item.set_item(value)
        menu.dismiss()


class AlgorithmConfigurationParameter(MDBoxLayout):
    def __init__(self, parameter_value, padding=[dp(10), 0, dp(10), 0], color=True):
        super().__init__()
        self.color = color
        self.parameter_value = parameter_value
        self.orientation = "vertical"
        self.padding = padding
        self.size_hint_x = 1
        self.adaptive_height = True
        self.md_bg_color = "#2F2F2F" if color else "#3F3F3F"
        self.parameters = []
        self.expand_button = CustomIconButton(icon="chevron-down", pos_hint={'center_y': 0.5}, ripple_scale=0,
                                              on_release=self.on_expand)
        if isinstance(parameter_value, TypeParameterValue):
            layout = TypeParameterLayout(parameter_value=parameter_value)
            layout.add_widget(self.expand_button)
            self.add_widget(layout)
        elif isinstance(parameter_value, SelectionParameterValue):
            layout = SelectionParameterLayout(parameter_value=parameter_value,
                                              callback=self.reload_selection_parameters)
            layout.add_widget(self.expand_button)
            self.add_widget(layout)
            if len(parameter_value.values) > 0:
                self.padding[3] = dp(10)
            for para in parameter_value.values:
                parameter = AlgorithmConfigurationParameter(para, color=not color)
                self.parameters.append(parameter)
                self.add_widget(parameter)
        elif isinstance(parameter_value, BooleanParameterValue):
            layout = BooleanParameterLayout(parameter_value=parameter_value)
            layout.add_widget(self.expand_button)
            self.add_widget(layout)
        else:
            raise ValueError(f'Parameter type not supported')
        desc_layout = MDBoxLayout(orientation="vertical", size_hint_x=1, adaptive_height=True, spacing=dp(10),
                                  padding=[0, 0, 0, dp(10)])
        desc_layout.add_widget(Divider(orientation="horizontal", width=dp(2), md_bg_color=(1, 1, 1, 1)))
        desc_layout.add_widget(CustomLabel(text="Description", pos_hint={'center_y': 0.5}))
        label = MDLabel(text=parameter_value.description, adaptive_height=True)
        label.bind(texture_size=lambda *x: label.setter("height")(
            label, label.texture_size[1]
        ))
        desc_layout.add_widget(label)
        self.desc_layout = desc_layout
        self.show_desc = False

    def reload_selection_parameters(self):
        """
        Only if argument is a SelectionParameterValue. The added sub-parameters will be removed and all current
        parameter values are added.
        """
        for parameter in self.parameters:
            self.remove_widget(parameter)
        if len(self.parameter_value.values) > 0:
            self.padding[3] = dp(10)
        for para in self.parameter_value.values:
            parameter = AlgorithmConfigurationParameter(para, color=not self.color)
            self.parameters.append(parameter)
            self.add_widget(parameter)
        # The description should be above the content.
        if self.show_desc:
            self.remove_widget(self.desc_layout)
            self.add_widget(self.desc_layout)

    def on_expand(self, *args):
        self.show_desc = not self.show_desc
        if self.show_desc:
            if isinstance(self.parameter_value, SelectionParameterValue) and len(self.parameter_value.values) > 0:
                self.padding[3] -= dp(10)
            self.add_widget(self.desc_layout)
            self.expand_button.icon = "chevron-up"
        else:
            if isinstance(self.parameter_value, SelectionParameterValue) and len(self.parameter_value.values) > 0:
                self.padding[3] += dp(10)
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
            self.container.add_widget(AlgorithmConfigurationParameter(parameter, padding=[dp(10), 0, dp(10), 0]))
