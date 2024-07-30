from planar_robotics_configurator.model.configurator_model import ConfiguratorModel
from planar_robotics_configurator.model.environment import MoverPreset
from planar_robotics_configurator.view.utils import NonEmptyTextField, CustomSnackbar, ScrollDialog


class MoverPresetCreationDialog(ScrollDialog):
    """
    Mover Preset Creation Dialog. User can create a new MoverPreset.
    """

    def __init__(self):
        self.name_field = NonEmptyTextField(hint_text="Name", pos_hint={"center_y": 0.5}, required=True)
        self.width_field = NonEmptyTextField(hint_text="Width", pos_hint={"center_y": 0.5}, required=True,
                                             helper_text="In meters", input_filter="float")
        self.length_field = NonEmptyTextField(hint_text="Length", pos_hint={"center_y": 0.5}, required=True,
                                              helper_text="In meters", input_filter="float")
        self.height_field = NonEmptyTextField(hint_text="Height", pos_hint={"center_y": 0.5}, required=True,
                                              helper_text="In meters", input_filter="float")
        self.mass_field = NonEmptyTextField(hint_text="Mass", pos_hint={"center_y": 0.5}, required=True,
                                            helper_text="In kilograms", input_filter="float")
        super().__init__("Mover-preset creation", confirm_text="Add")

    def add_dialog_content(self):
        self.add_scroll_widget(self.name_field)
        self.add_scroll_widget(self.width_field)
        self.add_scroll_widget(self.length_field)
        self.add_scroll_widget(self.height_field)
        self.add_scroll_widget(self.mass_field)
        super().add_dialog_content()

    def check_name(self) -> bool:
        """
        Checks if the current entered name is already used.
        """
        preset_names = list(map((lambda preset: preset.name), ConfiguratorModel().mover_presets))
        return self.name_field.text not in preset_names

    def on_confirm(self):
        """
        When user confirms the dialog. Checks if all fields are filled and if the name already exists.
        When these conditions are fulfilled creates a new mover-preset and closes the dialog.
        """
        if not self.check_fields():
            CustomSnackbar(text="Please fill out all fields").open()
            return
        if not self.check_name():
            CustomSnackbar(text="This name is already used").open()
            return
        ConfiguratorModel().mover_presets.append(MoverPreset(name=self.name_field.text,
                                                             width=float(self.width_field.text),
                                                             length=float(self.length_field.text),
                                                             height=float(self.height_field.text),
                                                             mass=float(self.mass_field.text)))
        self.dismiss()
