from kivy.metrics import dp
from kivy.uix.checkbox import CheckBox
from kivymd.uix.boxlayout import MDBoxLayout
from kivymd.uix.button import MDFlatButton
from kivymd.uix.dialog import MDDialog

from planar_robotics_configurator.model.environment.mover import Mover
from planar_robotics_configurator.view.utils import CustomLabel, NonEmptyTextField, CustomSnackbar


class DialogContent(MDBoxLayout):
    """
    Box layout for the dialog content.
    Adds all needed fields for the mover settings.
    """

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.orientation = "vertical"
        self.adaptive_height = True
        self.spacing = dp(10)

        self.add_widget(CustomLabel(text="Circle", pos_hint={"center_y": 0.5}))
        self.circle_layout = MDBoxLayout(orientation="horizontal", adaptive_height=True, spacing=dp(20))
        self.circle_checkbox = CheckBox(size_hint=(None, None), width=dp(20), height=dp(20), pos_hint={"center_y": 0.5})
        self.circle_checkbox.bind(active=self.on_circle_check)
        self.circle_layout.add_widget(self.circle_checkbox)
        self.radius_field = NonEmptyTextField(text="0", hint_text="Radius", helper_text="In centimeters",
                                              input_filter="float", pos_hint={"center_y": 0.5})
        self.circle_layout.add_widget(self.radius_field)
        self.add_widget(self.circle_layout)

        self.add_widget(CustomLabel(text="Box", pos_hint={"center_y": 0.5}))
        self.box_layout = MDBoxLayout(orientation="horizontal", adaptive_height=True, spacing=dp(20))
        self.box_checkbox = CheckBox(size_hint=(None, None), width=dp(20), height=dp(20), pos_hint={"center_y": 0.5})
        self.box_checkbox.bind(active=self.on_box_check)
        self.box_layout.add_widget(self.box_checkbox)
        self.width_field = NonEmptyTextField(text="0", hint_text="Width", helper_text="In centimeters",
                                             input_filter="float", pos_hint={"center_y": 0.5})
        self.box_layout.add_widget(self.width_field)
        self.length_field = NonEmptyTextField(text="0", hint_text="Length", required=True, helper_text="In centimeters",
                                              input_filter="float", pos_hint={"center_y": 0.5})
        self.box_layout.add_widget(self.length_field)
        self.add_widget(self.box_layout)

    def on_circle_check(self, checkbox, value):
        """
        Sets the box checkbox to inactive.
        """
        if value:
            self.box_checkbox.active = False

    def on_box_check(self, checkbox, value):
        """
        Sets the circle checkbox to inactive.
        """
        if value:
            self.circle_checkbox.active = False


class MoverSettingsDialog(MDDialog):
    """
    Mover settings dialog. Creates a dialog in which the user can input the settings of a mover.
    See DialogContent for more information.
    """

    def __init__(self, env_map, mover_x, mover_y, preset, mover=None):
        self.env_map = env_map
        self.mover_x = mover_x
        self.mover_y = mover_y
        self.preset = preset
        self.mover = mover
        self.dialog_content = DialogContent()
        self.title = "Mover Settings" if mover is not None else "Mover Creation"
        super().__init__(type="custom",
                         content_cls=self.dialog_content,
                         buttons=[
                             MDFlatButton(
                                 text="Cancel" if mover is None else "Delete",
                                 on_release=lambda *args: self.cancel()
                             ),
                             MDFlatButton(
                                 text="Add" if mover is None else "Edit",
                                 theme_text_color="Custom",
                                 text_color=(0, 0, 0, 1),
                                 md_bg_color=(1, 1, 1, 1),
                                 on_release=lambda *args: self.confirm()
                             )
                         ])
        if mover is not None:
            self.load_mover()
        self.update_height()

    def load_mover(self):
        """
        Load the collision_shape of the mover into the text fields.
        """
        match len(self.mover.collision_shape):
            case 0:
                return
            case 1:
                self.dialog_content.circle_checkbox.active = True
                self.dialog_content.radius_field.text = str(self.mover.collision_shape[0])
            case 2:
                self.dialog_content.box_checkbox.active = True
                self.dialog_content.width_field.text = str(self.mover.collision_shape[0])
                self.dialog_content.length_field.text = str(self.mover.collision_shape[1])

    def confirm(self):
        """
        When user presses the confirm button in the dialog.
        Checks if the mover is valid which means that the fields of the selected mode are filled out.
        Creates or updates mover and adds the mover to the current environment and draw it.
        """
        if self.mover is None:
            mover = Mover(self.preset, self.mover_x, self.mover_y, [])
        else:
            mover = self.mover
        if self.dialog_content.circle_checkbox.active:
            if self.dialog_content.radius_field.is_empty():
                CustomSnackbar(text="Please insert a radius").open()
                return
            mover.collision_shape = [float(self.dialog_content.radius_field.text)]
        elif self.dialog_content.box_checkbox.active:
            if self.dialog_content.width_field.is_empty() or self.dialog_content.length_field.is_empty():
                CustomSnackbar(text="Please insert a width and length").open()
                return
            mover.collision_shape = [float(self.dialog_content.width_field.text),
                                     float(self.dialog_content.length_field.text)]
        else:
            mover.collision_shape = []
        if self.mover is None:
            self.env_map.environment.movers.append(mover)
            self.env_map.draw_mover(mover)
            self.env_map.remove_hover_rect()
        self.dismiss()

    def cancel(self):
        """
        When user presses the cancel button in the dialog.
        Deletes (remove from environment and remove from map) the mover if one already exists.
        """
        if self.mover is not None:
            self.env_map.remove_mover(self.mover)
            self.env_map.remove_hover_rect()
            self.env_map.environment.movers.remove(self.mover)
        self.dismiss()
