from kivy.core.window import Window
from kivy.metrics import dp
from kivymd.uix.boxlayout import MDBoxLayout
from kivymd.uix.button import MDFlatButton
from kivymd.uix.dialog import MDDialog
from kivymd.uix.scrollview import MDScrollView

from planar_robotics_configurator.model.configurator_model import ConfiguratorModel
from planar_robotics_configurator.model.environment.environment import Environment
from planar_robotics_configurator.view.utils import CustomLabel, NonEmptyTextField
from planar_robotics_configurator.view.utils.custom_snackbar import CustomSnackbar


class DialogContent(MDBoxLayout):
    """
    Box layout for the dialog content.
    Adds all needed fields for the environment configuration.
    """

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.orientation = "vertical"
        self.adaptive_height = True
        self.spacing = dp(10)
        self.env_name = NonEmptyTextField(hint_text="Configuration name", required=True)
        self.add_widget(self.env_name)
        self.add_widget(CustomLabel(text="Environment"))
        self.env_width = NonEmptyTextField(text="10", hint_text="Width", helper_text="Number of tiles",
                                           required=True, input_filter="int")
        self.add_widget(self.env_width)
        self.env_length = NonEmptyTextField(text="10", hint_text="Length", helper_text="Number of tiles",
                                            required=True, input_filter="int")
        self.add_widget(self.env_length)
        self.table_height = NonEmptyTextField(text="40", hint_text="Table height", required=True,
                                              helper_text="In centimeters", input_filter="float")
        self.add_widget(self.table_height)
        self.std_noise = NonEmptyTextField(text="0.00001", hint_text="Std noise", required=True, input_filter="float")
        self.add_widget(self.std_noise)
        self.add_widget(CustomLabel(text="Tiles"))
        self.tiles_width = NonEmptyTextField(text="24", hint_text="Width", required=True,
                                             helper_text="In centimeters", input_filter="float")
        self.add_widget(self.tiles_width)
        self.tiles_length = NonEmptyTextField(text="24", hint_text="Length", required=True,
                                              helper_text="In centimeters", input_filter="float")
        self.add_widget(self.tiles_length)
        self.tiles_height = NonEmptyTextField(text="6.7", hint_text="Height", required=True,
                                              helper_text="In centimeters", input_filter="float")
        self.add_widget(self.tiles_height)
        self.tiles_mass = NonEmptyTextField(text="5.6", hint_text="Mass", required=True,
                                            helper_text="In kilograms", input_filter="float")
        self.add_widget(self.tiles_mass)


class EnvironmentSettingsDialog(MDDialog):
    """
    Environment settings dialog. Creates a dialog in which the user can input an environment configuration.
    See DialogContent for more information.
    """

    def __init__(self, env_component, environment: Environment = None):
        self.env_component = env_component
        self.environment = environment
        scroll = MDScrollView(size_hint_y=None, height=Window.height / 2)
        self.dialog_content = DialogContent()
        self.title = "Environment Settings"
        super().__init__(type="custom",
                         content_cls=scroll,
                         buttons=[
                             MDFlatButton(
                                 text="Cancel",
                                 on_release=lambda *x: self.dismiss()
                             ),
                             MDFlatButton(
                                 text="Confirm",
                                 theme_text_color="Custom",
                                 text_color=(0, 0, 0, 1),
                                 md_bg_color=(1, 1, 1, 1),
                                 on_release=lambda *x: self.confirm()
                             )
                         ])
        self.content_cls.add_widget(self.dialog_content)
        if self.environment is not None:
            self.load_environment()
        self.update_height()

    def load_environment(self):
        """
        Loads the environment into the dialog.
        """
        environment = self.environment
        self.dialog_content.env_name.text = environment.name
        self.dialog_content.env_width.text = str(environment.num_width)
        self.dialog_content.env_length.text = str(environment.num_length)
        self.dialog_content.table_height.text = str(environment.table_height)
        self.dialog_content.std_noise.text = f"{environment.std_noise:.10f}"
        self.dialog_content.tiles_width.text = str(environment.tile_width)
        self.dialog_content.tiles_length.text = str(environment.tile_length)
        self.dialog_content.tiles_height.text = str(environment.tile_height)
        self.dialog_content.tiles_mass.text = str(environment.tile_mass)

    def confirm(self):
        """
        When user presses the confirm button on the dialog.
        checks if the environment is valid which means that all names are not empty.
        Checks if name is already used.
        Creates or updates environment and sets ths environment as current.
        """
        for child in self.dialog_content.children:
            if not isinstance(child, NonEmptyTextField):
                continue
            if not child.is_empty():
                continue
            CustomSnackbar(text="Please fill out all fields!").open()
            return
        if not self.check_name():
            CustomSnackbar(text="This name is already used!").open()
            return
        if self.environment is None:
            environment = self.create_environment()
        else:
            environment = self.update_environment()
        self.env_component.set_environment(environment)
        self.dismiss()

    def check_name(self) -> bool:
        """
        Checks if the entered name is already used by another environment.
        returns True if the entered name is already used by another environment else False.
        """
        env_names = list(map((lambda env: env.name),
                             filter((lambda env: env != self.environment), ConfiguratorModel().environments)))
        return self.dialog_content.env_name.text not in env_names

    def create_environment(self) -> Environment:
        """
        Creates a new environment from the entered input fields.
        Adds the environment to the environments list.
        returns the environment object.
        """
        environment = Environment(name=self.dialog_content.env_name.text,
                                  num_width=int(self.dialog_content.env_width.text),
                                  num_length=int(self.dialog_content.env_length.text),
                                  table_height=float(self.dialog_content.table_height.text),
                                  std_noise=float(self.dialog_content.std_noise.text),
                                  tile_width=float(self.dialog_content.tiles_width.text),
                                  tile_length=float(self.dialog_content.tiles_length.text),
                                  tile_height=float(self.dialog_content.tiles_height.text),
                                  tile_mass=float(self.dialog_content.tiles_mass.text))
        ConfiguratorModel().environments.append(environment)
        return environment

    def update_environment(self) -> Environment:
        """
        Updates the environment from the entered input fields.
        """
        environment = self.environment
        environment.name = self.dialog_content.env_name.text
        environment.set_size(int(self.dialog_content.env_width.text), int(self.dialog_content.env_length.text))
        environment.table_height = float(self.dialog_content.table_height.text)
        environment.std_noise = float(self.dialog_content.std_noise.text)
        environment.tile_width = float(self.dialog_content.tiles_width.text)
        environment.tile_length = float(self.dialog_content.tiles_length.text)
        environment.tile_height = float(self.dialog_content.tiles_height.text)
        environment.tile_mass = float(self.dialog_content.tiles_mass.text)
        return environment
