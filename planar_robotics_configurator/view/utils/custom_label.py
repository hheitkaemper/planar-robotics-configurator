from kivymd.uix.button import MDFlatButton


class CustomLabel(MDFlatButton):
    """
    Custom label that displays a text without any issues on line-breaks or shorten.
    Actual a button with a transparent background color amd disabled touch events.
    """

    def __init__(self, **kwargs):
        self.md_bg_color = (0, 0, 0, 0)
        self.font_size = 16
        super().__init__(**kwargs)

    def on_press(self):
        pass

    def on_touch_down(self, touch):
        pass
