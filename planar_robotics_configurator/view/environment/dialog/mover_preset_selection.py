from kivy.metrics import dp
from kivymd.uix.boxlayout import MDBoxLayout
from kivymd.uix.button import MDFlatButton

from planar_robotics_configurator.model.configurator_model import ConfiguratorModel
from planar_robotics_configurator.view.environment.dialog import MoverPresetCreationDialog
from planar_robotics_configurator.view.environment.draw_mode import MoverMode
from planar_robotics_configurator.view.utils import CustomLabel, Divider, CustomSnackbar, ScrollDialog, CustomCheckbox


class MoverPresetSelectionDialog(ScrollDialog):
    """
    Dialog which allows the user to select a mover preset and switch to the mover mode.
    """

    def __init__(self, env_map):
        self.env_map = env_map
        self.preset = env_map.draw_mode.preset if isinstance(env_map.draw_mode, MoverMode) else None
        super().__init__("Mover-preset selection", "Cancel", "Select")

    def on_confirm(self):
        """
        When user select a preset at the dialog. Closes the dialog and allows the user to place movers with this preset.
        """
        if self.preset is None:
            CustomSnackbar(text="Please select a preset").open()
            return
        self.env_map.set_movers_mode(self.preset)
        self.dismiss()

    def on_cancel(self):
        """
        When user cancels the dialog. Closes the dialog and allows the user to place and remove tiles at the map.
        """
        self.dismiss()

    def add_dialog_content(self):
        for preset in ConfiguratorModel().mover_presets:
            if len(self.get_scroll_children()) > 0:
                self.add_scroll_widget(Divider(orientation="horizontal", width=dp(2), md_bg_color=(1, 1, 1, 1)))
            layout = MDBoxLayout(orientation="horizontal", adaptive_height=True, spacing=dp(20))
            checkbox = CheckBoxWithPreset(preset, size_hint=(None, None), width=dp(20), height=dp(20),
                                          pos_hint={"center_y": 0.5}, active=True if self.preset == preset else False)
            checkbox.bind(active=self.on_check)
            layout.add_widget(checkbox)
            layout.add_widget(MDBoxLayout(
                CustomLabel(text=preset.name, pos_hint={"center_y": 0.5}),
                CustomLabel(
                    text=f"Size: {preset.width}cm x {preset.length}cm x {preset.height}cm, Mass: {preset.mass}kg",
                    pos_hint={"center_y": 0.5}), orientation="vertical", adaptive_height=True))
            self.add_scroll_widget(layout)

        self.add_scroll_widget(MDFlatButton(text="Create preset", pos_hint={"center_x": 0.5, "center_y": 0.5},
                                            theme_text_color="Custom", text_color=(0, 0, 0, 1),
                                            md_bg_color=(1, 1, 1, 1),
                                            on_release=lambda *args: self.open_preset_creation()))

    def open_preset_creation(self):
        """
        Closes the current dialog and opens the preset creation dialog.
        """
        self.dismiss()
        MoverPresetCreationDialog().open()

    def on_check(self, checkbox, value):
        """
        Called when checkbox is clicked. Sets all checkboxes to False but the checked one.
        """
        if not value:
            if checkbox.preset == self.preset:
                self.preset = None
            return
        self.preset = checkbox.preset
        for layout in self.get_scroll_children():
            if not isinstance(layout, MDBoxLayout):
                continue
            for c in layout.children:
                if not isinstance(c, CheckBoxWithPreset):
                    continue
                if c == checkbox:
                    continue
                c.active = False


class CheckBoxWithPreset(CustomCheckbox):
    """
    A CheckBox in which a mover preset can be stored.
    """

    def __init__(self, preset, **kwargs):
        super().__init__(**kwargs)
        self.preset = preset
