from kivy.core.window import Window
from kivy.metrics import dp
from kivy.uix.widget import Widget
from kivymd.uix.boxlayout import MDBoxLayout
from kivymd.uix.button import MDFlatButton
from kivymd.uix.dialog import MDDialog
from kivymd.uix.scrollview import MDScrollView

from planar_robotics_configurator.view.utils import NonEmptyTextField


class ScrollDialog(MDDialog):

    def __init__(self, title, cancel_text="Cancel", confirm_text="Confirm"):
        self.title = title
        self.dialog_content = MDBoxLayout(orientation="vertical", adaptive_height=True, spacing=dp(10))
        super().__init__(type="custom",
                         content_cls=MDScrollView(size_hint_y=None, height=Window.height / 2),
                         buttons=[
                             MDFlatButton(
                                 text=cancel_text,
                                 on_release=lambda *x: self.on_cancel()
                             ),
                             MDFlatButton(
                                 text=confirm_text,
                                 theme_text_color="Custom",
                                 text_color=(0, 0, 0, 1),
                                 md_bg_color=(1, 1, 1, 1),
                                 on_release=lambda *x: self.on_confirm()
                             )
                         ])
        self.add_dialog_content()
        self.content_cls.add_widget(self.dialog_content)

    def on_confirm(self):
        self.dismiss()

    def on_cancel(self):
        self.dismiss()

    def add_dialog_content(self):
        pass

    def add_scroll_widget(self, widget):
        self.dialog_content.add_widget(widget)

    def get_scroll_children(self):
        return self.dialog_content.children

    def check_fields(self) -> bool:
        for child in self.get_scroll_children():
            if not isinstance(child, NonEmptyTextField):
                continue
            if not child.is_empty():
                continue
            return False
        return True

    def check_fields_recursive(self):
        return self._check_fields_recursive(self)

    def _check_fields_recursive(self, widget: Widget):
        if isinstance(widget, NonEmptyTextField):
            return not widget.is_empty()
        for child in widget.children:
            if not self._check_fields_recursive(child):
                return False
        return True
