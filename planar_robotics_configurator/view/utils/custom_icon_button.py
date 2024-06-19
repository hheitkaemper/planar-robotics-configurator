from kivymd.uix.button import MDIconButton


class CustomIconButton(MDIconButton):
    """
    Custom icon button with smaller padding and custom icon color.
    """

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self._default_icon_pad /= 4
        self.theme_text_color = "Custom"
        self.text_color = (1, 1, 1, 1)
