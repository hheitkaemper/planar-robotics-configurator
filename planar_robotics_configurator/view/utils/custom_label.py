from kivymd.uix.label import MDLabel


class CustomLabel(MDLabel):
    """
    Custom label that displays a text without any issues on line-breaks or shorten.
    """

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.adaptive_size = True
        self.bind(texture_size=lambda *x: self.setter("width")(
            self, self.texture_size[0]
        ))
        self.bind(texture_size=lambda *x: self.setter("height")(
            self, self.texture_size[1]
        ))
