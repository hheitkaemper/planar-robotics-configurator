from kivymd.uix.textfield import MDTextField


class NonEmptyTextField(MDTextField):

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.line_color_focus = (1, 1, 1, 1)
        self.text_color_focus = (1, 1, 1, 1)
        self.hint_text_color_focus = (1, 1, 1, 1)
        self.write_tab = False

    def is_empty(self) -> bool:
        if not self.required:
            return False
        return len(self.text.strip()) == 0
