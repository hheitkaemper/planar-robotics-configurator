from kivy.metrics import dp
from kivymd.uix.snackbar import MDSnackbar

from planar_robotics_configurator.view.utils import CustomLabel


class CustomSnackbar(MDSnackbar):
    """
    Custom snackbar which has the length of the text and is positioned at the bottom middle of the screen.
    """

    def __init__(self, text):
        super().__init__()
        self.y = dp(10)
        self.pos_hint = {'center_x': 0.5}
        label = CustomLabel(text=text)
        self.adaptive_width = True
        label.bind(width=lambda *x: self.setter("width")(label, label.width + label.x * 2))
        self.add_widget(label)
