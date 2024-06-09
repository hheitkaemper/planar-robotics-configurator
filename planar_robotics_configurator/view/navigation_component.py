from kivy.uix.widget import Widget
from kivymd.uix.floatlayout import MDFloatLayout
from kivymd.uix.tab import MDTabs, MDTabsBase


class Tab(MDFloatLayout, MDTabsBase):
    pass


class NavigationComponent(MDTabs):
    def __init__(self, **kwargs):
        super(NavigationComponent, self).__init__(**kwargs)
        self.background_color = "2F2F2F"

    def add_tab(self, title, widget: Widget) -> None:
        tab = Tab(title=title)
        tab.add_widget(widget)
        self.add_widget(tab)
