from kivymd.uix.boxlayout import MDBoxLayout
from kivymd.uix.label import MDLabel


class ImportContainer(MDBoxLayout):

    def __init__(self):
        super().__init__()
        self.size_hint = 1, 1
        self.add_widget(MDLabel(text="Import Container"))
