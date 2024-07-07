from kivymd.uix.button import MDIconButton
from kivymd.uix.tooltip import MDTooltip


class CustomIconButton(MDIconButton, MDTooltip):
    """
    Custom icon button with smaller padding and custom icon color.
    """

    def __init__(self, **kwargs):
        self._default_icon_pad /= 4
        self.theme_text_color = "Custom"
        self.text_color = (1, 1, 1, 1)
        self.old_text_color = (1, 1, 1, 1)
        self.tooltip_display_delay = 1
        super().__init__(**kwargs)

    def on_enter(self, *args):
        self.old_text_color = self.text_color
        self.text_color = (0.5, 0.5, 0.5, 1)
        super().on_enter(args)

    def on_leave(self):
        self.text_color = self.old_text_color
        super().on_leave()
