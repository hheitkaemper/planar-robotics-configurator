from kivy.metrics import dp
from kivymd.uix.boxlayout import MDBoxLayout
from kivymd.uix.button import MDFlatButton
from kivymd.uix.floatlayout import MDFloatLayout
from kivymd.uix.scrollview import MDScrollView
from kivymd.uix.widget import MDWidget

from planar_robotics_configurator.view.import_export.export_container import ExportContainer
from planar_robotics_configurator.view.import_export.import_container import ImportContainer
from planar_robotics_configurator.view.utils import Component


class ImportExportComponent(Component, MDFloatLayout):

    def __init__(self):
        super().__init__()
        self.size_hint = 1, 1
        self.layout = MDBoxLayout(orientation="vertical", size_hint=(0.5, 0.9), spacing=dp(10),
                                  radius=(dp(10), dp(10), dp(10), dp(10)),
                                  pos_hint={"center_x": .5, "center_y": .5}, padding=(dp(10), dp(10), dp(10), dp(10)))
        self.layout.md_bg_color = "#2F2F2F"
        self.import_button = MDFlatButton(text="Import", on_release=lambda _: self.on_import_select(),
                                          md_bg_color=(0.6, 0.6, 0.6, 1), padding=(dp(20), dp(8), dp(20), dp(8)),
                                          rounded_button=True)
        self.import_button.padding = (dp(20), dp(8), dp(20), dp(8))
        self.export_button = MDFlatButton(text="Export", on_release=lambda _: self.on_export_select(),
                                          md_bg_color=(0.3, 0.3, 0.3, 1), padding=(dp(20), dp(8), dp(20), dp(8)),
                                          rounded_button=True)
        self.layout.add_widget(
            MDBoxLayout(
                MDWidget(),
                self.import_button,
                self.export_button,
                MDWidget(),
                adaptive_height=True, size_hint_x=1, orientation="horizontal", spacing=dp(10),
                pos_hint={"center_x": .5, "center_y": .5}))
        self.import_container = ImportContainer()
        self.export_container = ExportContainer()
        self.scroll = MDScrollView(size_hint=(1, 1))
        self.scroll.add_widget(self.import_container)
        self.layout.add_widget(self.scroll)
        self.add_widget(self.layout)
        pass

    def on_import_select(self):
        self.scroll.remove_widget(self.export_container)
        self.scroll.remove_widget(self.import_container)
        self.import_button.md_bg_color = (0.6, 0.6, 0.6, 1)
        self.export_button.md_bg_color = (0.3, 0.3, 0.3, 1)
        self.scroll.add_widget(self.import_container)

    def on_export_select(self):
        self.scroll.remove_widget(self.import_container)
        self.scroll.remove_widget(self.export_container)
        self.import_button.md_bg_color = (0.3, 0.3, 0.3, 1)
        self.export_button.md_bg_color = (0.6, 0.6, 0.6, 1)
        self.scroll.add_widget(self.export_container)
        self.export_container.reset()

    def on_select(self, _):
        self.export_container.reset()
        pass
