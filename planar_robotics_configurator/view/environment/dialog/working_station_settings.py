from typing import Union

from kivy.metrics import dp
from kivymd.uix.boxlayout import MDBoxLayout
from kivymd.uix.button import MDFlatButton
from kivymd.uix.dialog import MDDialog
from kivymd.uix.pickers import MDColorPicker
from plyer import filechooser

from planar_robotics_configurator.model.environment.working_station import WorkingStation
from planar_robotics_configurator.view.utils import NonEmptyTextField, CustomSnackbar, CustomIconButton


class DialogContent(MDBoxLayout):
    """
    Box layout for the dialog content.
    Adds all needed fields for the working station settings.
    """

    def __init__(self, x, y, z, **kwargs):
        super().__init__(**kwargs)
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

        file_layout = MDBoxLayout(orientation="horizontal", adaptive_height=True, spacing=dp(20))
        self.file_name = NonEmptyTextField(hint_text="File", pos_hint={"center_y": 0.5}, required=True)
        file_layout.add_widget(self.file_name)
        file_layout.add_widget(CustomIconButton(icon="folder", pos_hint={"center_y": 0.5},
                                                tooltip_text="Select file", on_release=self.open_file_selection))
        self.add_widget(file_layout)

        self.pos_layout = MDBoxLayout(orientation="horizontal", adaptive_height=True, spacing=dp(20))
        self.x_field = NonEmptyTextField(text=str(x), hint_text="X", helper_text="In centimeters",
                                         input_filter="float", pos_hint={"center_y": 0.5})
        self.pos_layout.add_widget(self.x_field)
        self.y_field = NonEmptyTextField(text=str(y), hint_text="Y", helper_text="In centimeters",
                                         input_filter="float", pos_hint={"center_y": 0.5})
        self.pos_layout.add_widget(self.y_field)
        self.z_field = NonEmptyTextField(text=str(z), hint_text="Z", helper_text="In centimeters",
                                         input_filter="float", pos_hint={"center_y": 0.5})
        self.pos_layout.add_widget(self.z_field)
        self.add_widget(self.pos_layout)

    def open_file_selection(self, *args):
        res = filechooser.open_file(title="Select file", filters=["*.xml"])
        if len(res) == 0:
            return
        self.file_name.text = res[0]

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


class WorkingStationSettings(MDDialog):
    """
    Working station settings dialog. Creates a dialog in which the user can input the settings of a working station.
    See DialogContent for more information.
    """

    def __init__(self, env_map, x=0, y=0, z=0, working_station=None):
        self.env_map = env_map
        self.working_station: WorkingStation | None = working_station
        if working_station is not None:
            x = working_station.position[0]
            y = working_station.position[1]
            z = working_station.position[2]
        self.dialog_content = DialogContent(x, y, z)
        self.title = "Working Station Settings" if working_station is not None else "Working Station Creation"
        super().__init__(type="custom",
                         content_cls=self.dialog_content,
                         buttons=[
                             MDFlatButton(
                                 text="Cancel" if working_station is None else "Delete",
                                 on_release=lambda *args: self.cancel()
                             ),
                             MDFlatButton(
                                 text="Add" if working_station is None else "Edit",
                                 theme_text_color="Custom",
                                 text_color=(0, 0, 0, 1),
                                 md_bg_color=(1, 1, 1, 1),
                                 on_release=lambda *args: self.confirm()
                             )
                         ])
        if working_station is not None:
            self.load_working_station()
        self.update_height()

    def load_working_station(self):
        self.dialog_content.name_field.text = self.working_station.name
        self.dialog_content.color_button.text_color = self.working_station.color
        self.dialog_content.file_name.text = self.working_station.fileRef
        self.dialog_content.x_field.text = str(self.working_station.position[0])
        self.dialog_content.y_field.text = str(self.working_station.position[1])
        self.dialog_content.z_field.text = str(self.working_station.position[2])

    def field_empty(self) -> bool:
        return (self.dialog_content.name_field.is_empty()
                or self.dialog_content.file_name.is_empty()
                or self.dialog_content.x_field.is_empty()
                or self.dialog_content.y_field.is_empty()
                or self.dialog_content.z_field.is_empty())

    def check_name(self) -> bool:
        """
        Checks if the current entered name is already used.
        """
        working_station_names = list(map((lambda working_station: working_station.name),
                                         filter(lambda working_station: working_station != self.working_station,
                                                self.env_map.environment.working_stations)))
        return self.dialog_content.name_field.text not in working_station_names

    def confirm(self):
        if self.field_empty():
            CustomSnackbar(text="Please fill out all fields").open()
            return
        if not self.check_name():
            CustomSnackbar(text="This name is already used").open()
            return
        if self.working_station is None:
            working_station = WorkingStation(self.dialog_content.name_field.text,
                                             self.dialog_content.file_name.text,
                                             (float(self.dialog_content.x_field.text),
                                              float(self.dialog_content.y_field.text),
                                              float(self.dialog_content.z_field.text)),
                                             self.dialog_content.color_button.text_color)
            self.env_map.environment.working_stations.append(working_station)
            self.env_map.draw_working_station(working_station)
        else:
            self.env_map.remove_working_station(self.working_station)
            self.working_station.name = self.dialog_content.name_field.text
            self.working_station.fileRef = self.dialog_content.file_name.text
            self.working_station.position = (float(self.dialog_content.x_field.text),
                                             float(self.dialog_content.y_field.text),
                                             float(self.dialog_content.z_field.text))
            self.working_station.color = self.dialog_content.color_button.text_color
            self.env_map.draw_working_station(self.working_station)
        self.dismiss()

    def cancel(self):
        if self.working_station is not None:
            self.env_map.remove_working_station(self.working_station)
            self.env_map.remove_hover_robot()
            self.env_map.environment.working_stations.remove(self.working_station)
        self.dismiss()
