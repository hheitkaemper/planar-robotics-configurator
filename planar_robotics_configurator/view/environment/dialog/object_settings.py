from typing import Union

from kivy.metrics import dp
from kivymd.uix.boxlayout import MDBoxLayout
from kivymd.uix.button import MDFlatButton
from kivymd.uix.dialog import MDDialog
from kivymd.uix.pickers import MDColorPicker
from plyer import filechooser

from planar_robotics_configurator.model.environment.object import Object, RefObject, CubeObject, BallObject
from planar_robotics_configurator.view.utils import NonEmptyTextField, CustomSnackbar, CustomIconButton, CustomCheckbox, \
    CustomLabel


class DialogContent(MDBoxLayout):
    """
    Box layout for the dialog content.
    Adds all needed fields for the object settings.
    """

    def __init__(self, x, y, z, dialog, **kwargs):
        super().__init__(**kwargs)
        self.dialog = dialog
        self.orientation = "vertical"
        self.adaptive_height = True
        self.spacing = dp(10)

        name_layout = MDBoxLayout(orientation="horizontal", adaptive_height=True, spacing=dp(20))
        self.name_field = NonEmptyTextField(hint_text="Name", pos_hint={"center_y": 0.5}, required=True)
        name_layout.add_widget(self.name_field)
        self.color_button = CustomIconButton(icon="palette", pos_hint={"center_y": 0.5}, tooltip_text="Select color",
                                             on_release=self.open_color_picker)
        name_layout.add_widget(self.color_button)
        self.add_widget(name_layout)

        self.pos_layout = MDBoxLayout(orientation="horizontal", adaptive_height=True, spacing=dp(20))
        self.x_field = NonEmptyTextField(text=str(x), hint_text="X", helper_text="In meters",
                                         input_filter="float", pos_hint={"center_y": 0.5})
        self.pos_layout.add_widget(self.x_field)
        self.y_field = NonEmptyTextField(text=str(y), hint_text="Y", helper_text="In meters",
                                         input_filter="float", pos_hint={"center_y": 0.5})
        self.pos_layout.add_widget(self.y_field)
        self.z_field = NonEmptyTextField(text=str(z), hint_text="Z", helper_text="In neters",
                                         input_filter="float", pos_hint={"center_y": 0.5})
        self.pos_layout.add_widget(self.z_field)
        self.add_widget(self.pos_layout)

        chip_layout = MDBoxLayout(orientation="horizontal", adaptive_height=True, spacing=dp(20))

        self.file_ref_button = CustomCheckbox(active=True)
        self.file_ref_button.bind(on_release=self.switch_checks)
        self.file_ref_button.bind(active=lambda instance, active: self.set_file_ref_mode() if active else None)
        chip_layout.add_widget(MDBoxLayout(
            self.file_ref_button,
            CustomLabel(text="Mujoco file", pos_hint={"center_y": 0.5}),
            orientation="horizontal", adaptive_height=True, spacing=dp(5)))

        self.cube_button = CustomCheckbox()
        self.cube_button.bind(on_release=self.switch_checks)
        self.cube_button.bind(active=lambda instance, active: self.set_cube_mode() if active else None)
        chip_layout.add_widget(MDBoxLayout(
            self.cube_button,
            CustomLabel(text="Cube", pos_hint={"center_y": 0.5}),
            orientation="horizontal", adaptive_height=True, spacing=dp(5)))

        self.ball_button = CustomCheckbox()
        self.ball_button.bind(on_release=self.switch_checks)
        self.ball_button.bind(active=lambda instance, active: self.set_ball_mode() if active else None)
        chip_layout.add_widget(MDBoxLayout(
            self.ball_button,
            CustomLabel(text="Ball", pos_hint={"center_y": 0.5}),
            orientation="horizontal", adaptive_height=True, spacing=dp(5)))

        self.add_widget(chip_layout)

        self.mode_layout = MDBoxLayout(orientation="horizontal", adaptive_height=True, spacing=dp(20))
        self.file_name = NonEmptyTextField(hint_text="File", helper_text="Mujoco Filepath", pos_hint={"center_y": 0.5},
                                           required=True)
        self.cube_width = NonEmptyTextField(hint_text="Width", helper_text="In meters", pos_hint={"center_y": 0.5},
                                            required=True, input_filter="float")
        self.cube_length = NonEmptyTextField(hint_text="Length", helper_text="In meters",
                                             pos_hint={"center_y": 0.5}, required=True, input_filter="float")
        self.cube_height = NonEmptyTextField(hint_text="Height", helper_text="In meters",
                                             pos_hint={"center_y": 0.5}, required=True, input_filter="float")
        self.ball_radius = NonEmptyTextField(hint_text="Radius", helper_text="In meters",
                                             pos_hint={"center_y": 0.5}, required=True, input_filter="float")
        self.friction = NonEmptyTextField(hint_text="Friction",
                                          pos_hint={"center_y": 0.5}, required=True, input_filter="float")
        self.set_file_ref_mode()
        self.add_widget(self.mode_layout)

    def open_color_picker(self, *args):
        self.color_picker = MDColorPicker(size_hint=(0.45, 0.85))
        self.color_picker.bind(on_release=self.get_selected_color)
        self.color_picker.open()

    def get_selected_color(self, instance_color_picker: MDColorPicker, type_color: str,
                           selected_color: Union[list, str]):
        if len(selected_color) < 4:
            return
        self.color_button.text_color = (selected_color[0], selected_color[1], selected_color[2], selected_color[3])
        self.color_picker.dismiss()

    def switch_checks(self, checkbox_instance):
        for i in [self.file_ref_button, self.cube_button, self.ball_button]:
            if checkbox_instance == i:
                continue
            i.active = False
        checkbox_instance.active = True

    def remove_all(self):
        self.mode_layout.clear_widgets()

    def set_file_ref_mode(self):
        self.remove_all()
        self.mode_layout.add_widget(self.file_name)
        self.mode_layout.add_widget(CustomIconButton(icon="folder", pos_hint={"center_y": 0.5},
                                                     tooltip_text="Select file", on_release=self.open_file_selection))

    def set_cube_mode(self):
        self.remove_all()
        self.mode_layout.add_widget(self.cube_width)
        self.mode_layout.add_widget(self.cube_length)
        self.mode_layout.add_widget(self.cube_height)
        self.mode_layout.add_widget(self.friction)

    def set_ball_mode(self):
        self.remove_all()
        self.mode_layout.add_widget(self.ball_radius)
        self.mode_layout.add_widget(self.friction)

    def open_file_selection(self, *args):
        res = filechooser.open_file(title="Select file", filters=["*.xml"])
        if res is None or len(res) == 0:
            return
        self.file_name.text = res[0]


class ObjectSettings(MDDialog):
    """
    Object settings dialog. Creates a dialog in which the user can input the settings of an object.
    The user can decide between different types of object: Mujoco file references, cubes and balls.
    See DialogContent for more information.
    """

    def __init__(self, env_map, x=0, y=0, z=0, object_instance=None):
        self.env_map = env_map
        self.object_instance: Object | None = object_instance
        if object_instance is not None:
            x = object_instance.position[0]
            y = object_instance.position[1]
            z = object_instance.position[2]
        self.dialog_content = DialogContent(x, y, z, self)
        self.title = "Object Settings" if object_instance is not None else "Object Creation"
        super().__init__(type="custom",
                         content_cls=self.dialog_content,
                         buttons=[
                             MDFlatButton(
                                 text="Cancel" if object_instance is None else "Delete",
                                 on_release=lambda *args: self.cancel()
                             ),
                             MDFlatButton(
                                 text="Add" if object_instance is None else "Edit",
                                 theme_text_color="Custom",
                                 text_color=(0, 0, 0, 1),
                                 md_bg_color=(1, 1, 1, 1),
                                 on_release=lambda *args: self.confirm()
                             )
                         ])
        if object_instance is not None:
            self.load_object()
        self.update_height()

    def load_object(self):
        self.dialog_content.name_field.text = self.object_instance.name
        self.dialog_content.color_button.text_color = self.object_instance.color
        self.dialog_content.x_field.text = str(self.object_instance.position[0])
        self.dialog_content.y_field.text = str(self.object_instance.position[1])
        self.dialog_content.z_field.text = str(self.object_instance.position[2])
        if isinstance(self.object_instance, RefObject):
            self.dialog_content.switch_checks(self.dialog_content.file_ref_button)
            self.dialog_content.set_file_ref_mode()
            self.dialog_content.file_name.text = self.object_instance.fileRef
        if isinstance(self.object_instance, CubeObject):
            self.dialog_content.switch_checks(self.dialog_content.cube_button)
            self.dialog_content.set_cube_mode()
            self.dialog_content.cube_width.text = str(self.object_instance.width)
            self.dialog_content.cube_length.text = str(self.object_instance.length)
            self.dialog_content.cube_height.text = str(self.object_instance.height)
            self.dialog_content.friction.text = str(self.object_instance.friction)
        if isinstance(self.object_instance, BallObject):
            self.dialog_content.switch_checks(self.dialog_content.ball_button)
            self.dialog_content.set_ball_mode()
            self.dialog_content.ball_radius.text = str(self.object_instance.radius)
            self.dialog_content.friction.text = str(self.object_instance.friction)

    def field_empty(self) -> bool:
        return (self.dialog_content.name_field.is_empty()
                or self.dialog_content.x_field.is_empty()
                or self.dialog_content.y_field.is_empty()
                or self.dialog_content.z_field.is_empty())

    def check_name(self) -> bool:
        """
        Checks if the current entered name is already used.
        """
        object_names = list(
            map((lambda o: o.name), filter(lambda o: o != self.object_instance, self.env_map.environment.objects)))
        return self.dialog_content.name_field.text not in object_names

    def confirm(self):
        if self.field_empty():
            CustomSnackbar(text="Please fill out all fields").open()
            return
        else:
            if self.dialog_content.file_ref_button.active and self.dialog_content.file_name.is_empty():
                CustomSnackbar(text="Please fill out all fields").open()
                return
            if self.dialog_content.cube_button.active and (
                    self.dialog_content.cube_width.is_empty()
                    or self.dialog_content.cube_length.is_empty()
                    or self.dialog_content.cube_height.is_empty()
                    or self.dialog_content.friction.is_empty()
            ):
                CustomSnackbar(text="Please fill out all fields").open()
                return
            if self.dialog_content.ball_button.active and (
                    self.dialog_content.ball_radius.is_empty() or self.dialog_content.friction.is_empty()):
                CustomSnackbar(text="Please fill out all fields").open()
                return
        if not self.check_name():
            CustomSnackbar(text="This name is already used").open()
            return
        if self.object_instance is not None:
            self.env_map.remove_object(self.object_instance)
            self.env_map.environment.objects.remove(self.object_instance)

        new_object_instance = None
        if self.dialog_content.file_ref_button.active:
            new_object_instance = RefObject(self.dialog_content.name_field.text,
                                            (float(self.dialog_content.x_field.text),
                                             float(self.dialog_content.y_field.text),
                                             float(self.dialog_content.z_field.text)
                                             ),
                                            self.dialog_content.color_button.text_color,
                                            self.dialog_content.file_name.text)
        if self.dialog_content.cube_button.active:
            new_object_instance = CubeObject(self.dialog_content.name_field.text,
                                             (float(self.dialog_content.x_field.text),
                                              float(self.dialog_content.y_field.text),
                                              float(self.dialog_content.z_field.text)
                                              ),
                                             self.dialog_content.color_button.text_color,
                                             float(self.dialog_content.cube_width.text),
                                             float(self.dialog_content.cube_length.text),
                                             float(self.dialog_content.cube_height.text),
                                             float(self.dialog_content.friction.text))
        if self.dialog_content.ball_button.active:
            new_object_instance = BallObject(self.dialog_content.name_field.text,
                                             (float(self.dialog_content.x_field.text),
                                              float(self.dialog_content.y_field.text),
                                              float(self.dialog_content.z_field.text)
                                              ),
                                             self.dialog_content.color_button.text_color,
                                             float(self.dialog_content.ball_radius.text),
                                             float(self.dialog_content.friction.text))
        if new_object_instance is not None:
            self.env_map.environment.objects.append(new_object_instance)
            self.env_map.draw_object(new_object_instance)
        self.dismiss()

    def cancel(self):
        if self.object_instance is not None:
            self.env_map.remove_object(self.object_instance)
            self.env_map.environment.objects.remove(self.object_instance)
        self.dismiss()
