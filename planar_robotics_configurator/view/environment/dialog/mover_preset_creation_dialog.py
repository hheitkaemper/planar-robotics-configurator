from kivy.core.window import Window
from kivy.metrics import dp
from kivymd.uix.boxlayout import MDBoxLayout
from kivymd.uix.button import MDFlatButton
from kivymd.uix.dialog import MDDialog
from kivymd.uix.scrollview import MDScrollView

from planar_robotics_configurator.model.configurator_model import ConfiguratorModel
from planar_robotics_configurator.model.environment import MoverPreset
from planar_robotics_configurator.view.utils import NonEmptyTextField, CustomSnackbar


class DialogContent(MDBoxLayout):
    """
    BoxLayout which has all fields which are needed for the creation of a MoverPreset.
    """

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.orientation = "vertical"
        self.adaptive_height = True
        self.spacing = dp(10)
        self.name_field = NonEmptyTextField(hint_text="Name", pos_hint={"center_y": 0.5}, required=True)
        self.add_widget(self.name_field)
        self.width_field = NonEmptyTextField(hint_text="Width", pos_hint={"center_y": 0.5}, required=True,
                                             helper_text="In centimeters", input_filter="float")
        self.add_widget(self.width_field)
        self.length_field = NonEmptyTextField(hint_text="Length", pos_hint={"center_y": 0.5}, required=True,
                                              helper_text="In centimeters", input_filter="float")
        self.add_widget(self.length_field)
        self.height_field = NonEmptyTextField(hint_text="Height", pos_hint={"center_y": 0.5}, required=True,
                                              helper_text="In centimeters", input_filter="float")
        self.add_widget(self.height_field)
        self.mass_field = NonEmptyTextField(hint_text="Mass", pos_hint={"center_y": 0.5}, required=True,
                                            helper_text="In kilograms", input_filter="float")
        self.add_widget(self.mass_field)


class MoverPresetCreationDialog(MDDialog):
    """
    Mover Preset Creation Dialog. User can create a new MoverPreset.
    """

    def __init__(self):
        scroll = MDScrollView(size_hint_y=None, height=Window.height / 2)
        self.dialog_content = DialogContent()
        self.title = "Mover-preset creation"
        super().__init__(type="custom",
                         content_cls=scroll,
                         buttons=[
                             MDFlatButton(
                                 text="Cancel",
                                 on_release=lambda *args: self.dismiss()
                             ),
                             MDFlatButton(
                                 text="Add", theme_text_color="Custom", text_color=(0, 0, 0, 1),
                                 md_bg_color=(1, 1, 1, 1), on_release=lambda *args: self.confirm()
                             )
                         ])
        self.content_cls.add_widget(self.dialog_content)
        self.update_height()

    def check_name(self) -> bool:
        """
        Checks if the current entered name is already used.
        """
        preset_names = list(map((lambda preset: preset.name), ConfiguratorModel().mover_presets))
        return self.dialog_content.name_field.text not in preset_names

    def confirm(self):
        """
        When user confirms the dialog. Checks if all fields are filled and if the name already exists.
        When these conditions are fulfilled creates a new mover-preset and closes the dialog.
        """
        for child in self.dialog_content.children:
            if not isinstance(child, NonEmptyTextField):
                continue
            if not child.is_empty():
                continue
            CustomSnackbar(text="Please fill out all fields").open()
            return
        if not self.check_name():
            CustomSnackbar(text="This name is already used").open()
            return
        ConfiguratorModel().mover_presets.append(MoverPreset(name=self.dialog_content.name_field.text,
                                                             width=float(self.dialog_content.width_field.text),
                                                             length=float(self.dialog_content.length_field.text),
                                                             height=float(self.dialog_content.height_field.text),
                                                             mass=float(self.dialog_content.mass_field.text)))
        self.dismiss()
