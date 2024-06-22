from kivymd.uix.textfield import MDTextField


class NonEmptyTextField(MDTextField):
    def is_empty(self) -> bool:
        return len(self.text.strip()) == 0
