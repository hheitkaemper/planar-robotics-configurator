from kivy.core.window import Window
from kivy.metrics import dp
from kivy.uix.checkbox import CheckBox
from kivymd.uix.boxlayout import MDBoxLayout
from kivymd.uix.button import MDFlatButton
from kivymd.uix.dialog import MDDialog
from kivymd.uix.scrollview import MDScrollView

from planar_robotics_configurator.model.configurator_model import ConfiguratorModel
from planar_robotics_configurator.view.environment.dialog import MoverPresetCreationDialog
from planar_robotics_configurator.view.utils import CustomLabel, Divider, CustomSnackbar


class CheckBoxWithPreset(CheckBox):
    """
    A CheckBox in which a mover preset can be stored.
    """

    def __init__(self, preset, **kwargs):
        super().__init__(**kwargs)
        self.preset = preset


class DialogContent(MDBoxLayout):
    """
    Box layout for the dialog content.
    Adds all needed fields for the mover preset selection.
    Creates an entry for each mover preset in the model.
    """

    def __init__(self, dialog, **kwargs):
        super().__init__(**kwargs)
        self.dialog = dialog
        self.preset = self.dialog.env_map.selected_mover_preset
        self.orientation = "vertical"
        self.adaptive_height = True
        self.spacing = dp(10)
        for preset in ConfiguratorModel().mover_presets:
            if len(self.children) > 0:
                self.add_widget(Divider(orientation="horizontal", width=dp(2), md_bg_color=(1, 1, 1, 1)))
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
            self.add_widget(layout)

        self.add_widget(MDFlatButton(text="Create preset", pos_hint={"center_x": 0.5, "center_y": 0.5},
                                     theme_text_color="Custom", text_color=(0, 0, 0, 1), md_bg_color=(1, 1, 1, 1),
                                     on_release=lambda *args: self.open_preset_creation()))

    def open_preset_creation(self):
        """
        Closes the current dialog and opens the preset creation dialog.
        """
        self.dialog.dismiss()
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
        for layout in self.children:
            if not isinstance(layout, MDBoxLayout):
                continue
            for c in layout.children:
                if not isinstance(c, CheckBoxWithPreset):
                    continue
                if c == checkbox:
                    continue
                c.active = False


class MoverPresetSelectionDialog(MDDialog):
    """
    Dialog which allows the user to select a mover preset and switch to the mover mode.
    """

    def __init__(self, env_map):
        self.env_map = env_map
        self.dialog_content = DialogContent(self)
        scroll = MDScrollView(size_hint_y=None, height=Window.height / 2)
        self.title = "Mover-preset selection"
        super().__init__(type="custom",
                         content_cls=scroll,
                         buttons=[
                             MDFlatButton(
                                 text="Tiles mode",
                                 on_release=lambda *args: self.cancel()
                             ),
                             MDFlatButton(
                                 text="Select",
                                 theme_text_color="Custom",
                                 text_color=(0, 0, 0, 1),
                                 md_bg_color=(1, 1, 1, 1),
                                 on_release=lambda *args: self.confirm()
                             )
                         ])
        scroll.add_widget(self.dialog_content)
        self.update_height()

    def cancel(self):
        """
        When user cancels the dialog. Closes the dialog and allows the user to place and remove tiles at the map.
        """
        self.env_map.set_tiles_mode()
        self.dismiss()

    def confirm(self):
        """
        When user select a preset at the dialog. Closes the dialog and allows the user to place movers with this preset.
        """
        if self.dialog_content.preset is None:
            CustomSnackbar(text="Please select a preset").open()
            return
        self.env_map.set_movers_mode(self.dialog_content.preset)
        self.dismiss()
