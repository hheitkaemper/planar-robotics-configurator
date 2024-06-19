from kivymd.uix.widget import MDWidget


class Divider(MDWidget):
    """
    Divider which can divide content with a horizontal or vertical line.
    The line width and orientation can be set.
    """

    def __init__(self, orientation, width, **kwargs):
        super().__init__(**kwargs)
        assert orientation in ["horizontal", "vertical"]
        if orientation == "horizontal":
            self.size_hint = 1, None
            self.height = width
        elif orientation == "vertical":
            self.size_hint = None, 1
            self.width = width
