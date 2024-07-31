from kivy.metrics import dp
from kivymd.uix.boxlayout import MDBoxLayout

from planar_robotics_configurator.model.configurator_model import ConfiguratorModel
from planar_robotics_configurator.model.environment import Environment
from planar_robotics_configurator.view.utils import CustomLabel, NonEmptyTextField, CustomSnackbar, ScrollDialog


class EnvironmentSettingsDialog(ScrollDialog):
    """
    Environment settings dialog. Creates a dialog in which the user can input an environment configuration.
    """

    def __init__(self, env_component, environment: Environment = None):
        self.env_component = env_component
        self.environment = environment

        self.env_name = NonEmptyTextField(hint_text="Configuration name", required=True)
        self.env_width = NonEmptyTextField(text="10", hint_text="Width", helper_text="Number of tiles", required=True,
                                           input_filter="int")
        self.env_length = NonEmptyTextField(text="10", hint_text="Length", helper_text="Number of tiles", required=True,
                                            input_filter="int")
        self.initial_mover_zpos = NonEmptyTextField(text="0.005", hint_text="Initial mover z-pos", required=True,
                                                    helper_text="In meters", input_filter="float")
        self.table_height = NonEmptyTextField(text="0.4", hint_text="Table height", required=True,
                                              helper_text="In meters", input_filter="float")
        self.std_noise = NonEmptyTextField(text="0.00001", hint_text="Std noise", required=True, input_filter="float")
        self.tiles_width = NonEmptyTextField(text="0.24", hint_text="Width", required=True, helper_text="In meters",
                                             input_filter="float")
        self.tiles_length = NonEmptyTextField(text="0.24", hint_text="Length", required=True,
                                              helper_text="In meters", input_filter="float")
        self.tiles_height = NonEmptyTextField(text="0.067", hint_text="Height", required=True,
                                              helper_text="In meters", input_filter="float")
        self.tiles_mass = NonEmptyTextField(text="5.6", hint_text="Mass", required=True, helper_text="In kilograms",
                                            input_filter="float")
        self.min_mass = NonEmptyTextField(text="-1", hint_text="Min Mass", required=True, helper_text="In kilograms",
                                          input_filter="float")
        self.max_mass = NonEmptyTextField(text="-1", hint_text="Max Mass", required=True, helper_text="In kilograms",
                                          input_filter="float")
        self.min_friction = NonEmptyTextField(text="-1", hint_text="Min Friction", required=True, input_filter="float")
        self.max_friction = NonEmptyTextField(text="-1", hint_text="Max Friction", required=True, input_filter="float")
        self.max_v = NonEmptyTextField(text="2.0", hint_text="Max Velocity", required=True, input_filter="float",
                                       helper_text="In meter per second")
        self.max_a = NonEmptyTextField(text="10.0", hint_text="Max Acceleration", required=True, input_filter="float",
                                       helper_text="In meter per second squared")

        super().__init__("Environment creation" if environment is None else "Environment settings",
                         confirm_text="Edit" if environment is not None else "Add")
        if self.environment is not None:
            self.load_environment()

    def add_dialog_content(self):
        self.add_scroll_widget(self.env_name)
        self.add_scroll_widget(CustomLabel(text="Environment"))
        self.add_scroll_widget(self.env_width)
        self.add_scroll_widget(self.env_length)
        self.add_scroll_widget(self.initial_mover_zpos)
        self.add_scroll_widget(self.table_height)
        self.add_scroll_widget(self.std_noise)
        self.add_scroll_widget(CustomLabel(text="Tiles"))
        self.add_scroll_widget(self.tiles_width)
        self.add_scroll_widget(self.tiles_length)
        self.add_scroll_widget(self.tiles_height)
        self.add_scroll_widget(self.tiles_mass)
        self.add_scroll_widget(CustomLabel(text="Movers"))
        self.add_scroll_widget(self.max_v)
        self.add_scroll_widget(self.max_a)
        self.add_scroll_widget(CustomLabel(text="Objects"))
        self.add_scroll_widget(MDBoxLayout(
            self.min_mass,
            self.max_mass,
            orientation="horizontal", size_hint_x=1, adaptive_height=True, spacing=dp(10)))
        self.add_scroll_widget(MDBoxLayout(
            self.min_friction,
            self.max_friction,
            orientation="horizontal", size_hint_x=1, adaptive_height=True, spacing=dp(10)))

    def load_environment(self):
        """
        Loads the environment into the dialog.
        """
        environment = self.environment
        self.env_name.text = environment.name
        self.env_width.text = str(environment.num_width)
        self.env_length.text = str(environment.num_length)
        self.initial_mover_zpos.text = str(environment.initial_mover_zpos)
        self.table_height.text = str(environment.table_height)
        self.std_noise.text = f"{environment.std_noise:.10f}"
        self.tiles_width.text = str(environment.tile_width)
        self.tiles_length.text = str(environment.tile_length)
        self.tiles_height.text = str(environment.tile_height)
        self.tiles_mass.text = str(environment.tile_mass)
        self.min_mass.text = str(environment.min_mass)
        self.max_mass.text = str(environment.max_mass)
        self.max_a.text = str(environment.max_a)
        self.max_v.text = str(environment.max_v)
        self.min_friction.text = str(environment.min_friction)
        self.max_friction.text = str(environment.max_friction)

    def on_confirm(self):
        """
        When user presses the confirm button on the dialog.
        checks if the environment is valid which means that all names are not empty.
        Checks if name is already used.
        Creates or updates environment and sets ths environment as current.
        """
        if not self.check_fields_recursive():
            CustomSnackbar(text="Please fill out all fields").open()
            return
        if not self.check_name():
            CustomSnackbar(text="This name is already used").open()
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
        return self.env_name.text not in env_names

    def create_environment(self) -> Environment:
        """
        Creates a new environment from the entered input fields.
        Adds the environment to the environments list.
        returns the environment object.
        """
        environment = Environment(name=self.env_name.text,
                                  num_width=int(self.env_width.text),
                                  num_length=int(self.env_length.text),
                                  initial_mover_zpos=float(self.initial_mover_zpos.text),
                                  table_height=float(self.table_height.text),
                                  std_noise=float(self.std_noise.text),
                                  tile_width=float(self.tiles_width.text),
                                  tile_length=float(self.tiles_length.text),
                                  tile_height=float(self.tiles_height.text),
                                  tile_mass=float(self.tiles_mass.text),
                                  min_mass=float(self.min_mass.text),
                                  max_mass=float(self.max_mass.text),
                                  max_a=float(self.max_a.text),
                                  max_v=float(self.max_v.text),
                                  min_friction=float(self.min_friction.text),
                                  max_friction=float(self.max_friction.text))
        ConfiguratorModel().environments.append(environment)
        return environment

    def update_environment(self) -> Environment:
        """
        Updates the environment from the entered input fields.
        """
        environment = self.environment
        environment.name = self.env_name.text
        environment.set_size(int(self.env_width.text), int(self.env_length.text))
        environment.initial_mover_zpos = float(self.initial_mover_zpos.text)
        environment.table_height = float(self.table_height.text)
        environment.std_noise = float(self.std_noise.text)
        environment.tile_width = float(self.tiles_width.text)
        environment.tile_length = float(self.tiles_length.text)
        environment.tile_height = float(self.tiles_height.text)
        environment.tile_mass = float(self.tiles_mass.text)
        environment.min_mass = float(self.min_mass.text)
        environment.max_mass = float(self.max_mass.text)
        environment.max_a = float(self.max_a.text)
        environment.max_v = float(self.max_v.text)
        environment.min_friction = float(self.min_friction.text)
        environment.max_friction = float(self.max_friction.text)
        return environment
