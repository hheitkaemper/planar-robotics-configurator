from kivymd.uix.boxlayout import MDBoxLayout
from kivymd.uix.label import MDLabel


class SimulationComponent(MDBoxLayout):
    def __init__(self):
        super().__init__()
        self.add_widget(MDLabel(text='Simulation Component', halign='center'))
