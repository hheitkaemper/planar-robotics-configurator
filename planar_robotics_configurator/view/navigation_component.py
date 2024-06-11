from kivymd.uix.floatlayout import MDFloatLayout
from kivymd.uix.tab import MDTabs, MDTabsBase


class Tab(MDFloatLayout, MDTabsBase):
    def __init__(self, widget, **kwargs):
        super(Tab, self).__init__(**kwargs)
        self.widget = widget


class NavigationComponent(MDTabs):
    def __init__(self, app, **kwargs):
        super(NavigationComponent, self).__init__(**kwargs)
        self.app = app
        self.lock_swiping = True
        self.anim_duration = 0
        self.background_color = "2F2F2F"
        self.size_hint = 1, None
        self.height = self.tab_bar_height

    def add_tab(self, title, widget) -> None:
        tab = Tab(title=title, widget=widget)
        self.add_widget(tab)

    def on_tab_switch(self, instance_tab, instance_tab_label, tab_text):
        self.app.set_view(instance_tab.widget)
