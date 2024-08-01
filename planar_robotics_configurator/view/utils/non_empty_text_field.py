from kivymd.uix.textfield import MDTextField


class NonEmptyTextField(MDTextField):

    def __init__(self, required=False, **kwargs):
        super().__init__(**kwargs)
        self.required_copy = required
        self.line_color_focus = (1, 1, 1, 1)
        self.text_color_focus = (1, 1, 1, 1)
        self.hint_text_color_focus = (1, 1, 1, 1)
        self.write_tab = False

    def on_focus(self, instance_text_field, focus: bool) -> None:
        if self.required_copy is not None and focus:
            self.required = self.required_copy
            self.required_copy = None
        super().on_focus(instance_text_field, focus)

    def is_empty(self) -> bool:
        if self.required_copy is not None:
            self.required = self.required_copy
            self.required_copy = None
        if not self.required:
            return False
        if len(self.text.strip()) == 0:
            self.on_focus(self, False)
            return True
        self.on_focus(self, False)
        return False
