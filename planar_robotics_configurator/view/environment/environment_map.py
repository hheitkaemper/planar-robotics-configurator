from kivy.core.window import Window
from kivy.graphics import Color, Rectangle
from kivy.graphics.transformation import Matrix
from kivy.input import MotionEvent
from kivy.uix.scatter import Scatter
from kivymd.uix.widget import MDWidget


class EnvironmentScatter(Scatter):

    def __init__(self, **kwargs):
        super(EnvironmentScatter, self).__init__(**kwargs)
        self.do_scale = False
        self.do_rotation = False
        self.auto_bring_to_front = False

    def on_transform(self, *args):
        super().on_transform(*args)

    def collide_point(self, x, y):
        return True

    def on_touch_down(self, touch: MotionEvent):
        if "button" not in touch.profile or touch.button not in ["middle", "right"]:
            return True
        Window.set_system_cursor("size_all")
        touch.grab(self)
        return super().on_touch_down(touch)

    def on_touch_up(self, touch: MotionEvent):
        if touch.grab_current == self:
            touch.ungrab(self)
            Window.set_system_cursor("arrow")
        return super().on_touch_up(touch)


class EnvironmentMap(MDWidget):

    def __init__(self):
        super().__init__()
        self.size_hint = 1, 1
        self.scatter = EnvironmentScatter()
        with self.scatter.canvas:
            Color(rgba=(1, 0, 0, 1))
            Rectangle(pos=(200, 200), size=(200, 200))
        self.add_widget(self.scatter)

    def on_touch_down(self, touch: MotionEvent):
        if not self.collide_point(*touch.pos):
            return
        if "button" in touch.profile and touch.button == "scrolldown":
            self.scale_at(1, *touch.pos)
            return True
        if "button" in touch.profile and touch.button == "scrollup":
            self.scale_at(-1, *touch.pos)
            return True
        return super().on_touch_down(touch)

    def scale_at(self, scale: float, x: float, y: float) -> None:
        scale = 2 ** scale
        self.scatter.apply_transform(
            Matrix().scale(scale, scale, scale),
            post_multiply=True,
            anchor=self.scatter.to_local(x, y)
        )
