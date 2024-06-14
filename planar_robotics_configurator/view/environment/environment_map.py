from kivy.core.window import Window
from kivy.graphics import Color, Rectangle
from kivy.graphics.context_instructions import Scale
from kivy.graphics.instructions import Canvas
from kivy.graphics.transformation import Matrix
from kivy.input import MotionEvent
from kivy.uix.scatter import Scatter
from kivymd.uix.widget import MDWidget

from planar_robotics_configurator.model.environment.environment import Environment


class EnvironmentScatter(Scatter):
    """
    Environment layer in which all environment objects are drawn.
    Is possible to transform in x and y direction by dragging the environment with right and middle click.
    """

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


class HoverTile(Rectangle):
    """
    Represents a rectangle for which it is possible to store the x and y position of the tile which it should represent.
    """

    def __init__(self, x, y, **kwargs):
        super(HoverTile, self).__init__(**kwargs)
        self.x = x
        self.y = y


class EnvironmentMap(MDWidget):
    """
    Defines a map which can be moved by middle and right click and zoomed with scroll-wheel.
    Thous transformations are automatically applied to all canvas which are drawn to self.scatter.
    Draws the given environment.
    """

    def __init__(self, environment):
        super().__init__()
        Window.bind(mouse_pos=self.on_mouse_over)
        self.size_hint = 1, 1
        self.scatter = EnvironmentScatter()
        self.environment: Environment | None = None
        # Kivy coordinate system to environment coordinate system
        with self.scatter.canvas.before:
            Scale(1, -1, 1)
        with self.scatter.canvas:
            self.scatter.tiles_background_canvas = Canvas()
            self.scatter.tiles_canvas = Canvas()
            self.hover_tile_color = Color(0, 0, 0, 0)
            self.hover_tile = HoverTile(-1, -1, pos=(0, 0), size=(1, 1))
        self.add_widget(self.scatter)
        if environment is not None:
            self.set_environment(environment)

    def on_touch_down(self, touch: MotionEvent):
        if not self.collide_point(*touch.pos):
            return
        if "button" in touch.profile and touch.button == "scrolldown":
            self.scale_at(1, *touch.pos)
            return True
        if "button" in touch.profile and touch.button == "scrollup":
            self.scale_at(-1, *touch.pos)
            return True
        if "button" in touch.profile and touch.button == "left" and self.environment is not None:
            pos = self.screen_to_tile_position(*touch.pos)
            if 0 <= pos[0] < self.environment.num_width and 0 <= pos[1] < self.environment.num_length:
                self.environment.set_tile(*pos, 1 - self.environment.get_tile(*pos))
                self.remove_hover_tile()
                self.redraw_tile(*pos)
                return True
        return super().on_touch_down(touch)

    def on_mouse_over(self, window, pos):
        """
        Event on mouse over. Draw hover tile if mouse is over the possible area of tiles.
        :param pos: position of mouse over, (x, y).
        """
        if self.environment is None:
            return
        pos = self.screen_to_tile_position(*pos)
        if 0 <= pos[0] < self.environment.num_width and 0 <= pos[1] < self.environment.num_length:
            self.draw_hover_tile(*pos)
        else:
            self.remove_hover_tile()

    def remove_hover_tile(self):
        """
        Hide the hover tile to the user. Removes the color and sets the position of the hover tile to (-1, -1)
        """
        self.hover_tile_color.a = 0
        self.hover_tile.x = -1
        self.hover_tile.y = -1

    def draw_hover_tile(self, x, y):
        """
        Draws a hover tile at position (x, y) in tile position.
        The hover tile color depends on presents of the hovered tile.
        :param x: x position of the hovered tile.
        :param y: y position of the hovered tile.
        """
        if self.hover_tile.x == x and self.hover_tile.y == y:
            return
        if self.environment.get_tile(x, y) == 1:
            # Red
            self.hover_tile_color.rgba = (1, 0.45, 0.45, 1)
        else:
            # Green
            self.hover_tile_color.rgba = (0.65, 1, 0.56, 1)
        self.hover_tile.x = x
        self.hover_tile.y = y
        self.hover_tile.pos = self.tile_position_to_scatter(x + 0.05, y + 0.05)
        self.hover_tile.size = self.environment_to_scatter(self.environment.tile_width * 0.9,
                                                           self.environment.tile_length * 0.9)

    def scale_at(self, scale: float, x: float, y: float) -> None:
        """
        Scales the map according to the given parameter.
        :param scale: Scale factor, gets scaled by 1.5^scale
        :param x: x scale position
        :param y: y scale position
        """
        scale = 1.5 ** scale
        self.scatter.apply_transform(
            Matrix().scale(scale, scale, scale),
            post_multiply=True,
            anchor=self.scatter.to_local(x, y)
        )

    def set_environment(self, environment: Environment):
        """
        Specifies which environment is being used. Draws the environment.
        :param environment: Environment which should be drawn.
        """
        self.environment = environment
        self.remove_hover_tile()
        self.draw_tiles_background()
        self.draw_tiles()

    def draw_tiles_background(self):
        """
        Draws a background for the tiles with the size of num_width*tile_width and num_length*tile_length.
        """
        self.scatter.tiles_background_canvas.clear()
        with self.scatter.tiles_background_canvas:
            Color(0.16, 0.16, 0.16, 1)
            Rectangle(pos=(0, 0),
                      size=self.tile_position_to_scatter(self.environment.num_width, self.environment.num_length))

    def redraw_tile(self, x, y) -> None:
        """
        Removes the specified tile from the environment and draw the tile again.
        :param x: x position of the tile.
        :param y: y position of the tile.
        """
        pos = self.tile_position_to_scatter(x + 0.05, y + 0.05)
        self.scatter.tiles_canvas.children[:] = [c for c in self.scatter.tiles_canvas.children
                                                 if not (isinstance(c, Rectangle) and c.pos == pos)]
        self.draw_tile(x, y)

    def draw_tile(self, x, y) -> None:
        """
        Draws the specified tile on the environment.
        :param x: x position of the tile.
        :param y: y position of the tile.
        """
        with self.scatter.tiles_canvas:
            if self.environment.get_tile(x, y) == 1:
                Color(0.49, 0.49, 0.49, 1)
            else:
                Color(0.2, 0.2, 0.2, 1)
            Rectangle(pos=self.tile_position_to_scatter(x + 0.05, y + 0.05),
                      size=self.environment_to_scatter(self.environment.tile_width * 0.9,
                                                       self.environment.tile_length * 0.9))

    def draw_tiles(self) -> None:
        """
        Draws all the tiles in the environment.
        """
        self.scatter.tiles_canvas.clear()
        for x in range(0, self.environment.num_width):
            for y in range(0, self.environment.num_length):
                self.draw_tile(x, y)

    def tile_position_to_scatter(self, x, y) -> (int, int):
        """
        Converts coordinates in tiles coordinate-system to scatter coordinate-system.
        Args:
            x: x coordinate in tiles coordinate-system.
            y: y coordinate in tiles coordinate-system.

        Returns:
            (x, y) with x, y in scatter coordinate-system.
        """
        x, y = self.tile_position_to_environment(x, y)
        return y, x

    def tile_position_to_environment(self, x, y) -> (int, int):
        """
        Converts coordinates in tiles coordinate-system to environment coordinate-system.
        Args:
            x: x coordinate in tiles coordinate-system.
            y: y coordinate in tiles coordinate-system.

        Returns:
            (x, y) with x, y in environment coordinate-system.
        """
        x = x * self.environment.tile_width
        y = y * self.environment.tile_length
        return x, y

    def screen_to_tile_position(self, x, y) -> (int, int):
        """
        Converts coordinates in screen coordinate-system to tile coordinate-system.
        Args:
            x: x coordinate on the screen.
            y: y coordinate on the screen.

        Returns:
            (x, y) with x, y in tiles coordinate-system.
        """
        x, y = self.screen_to_environment(x, y)
        x = int(x // self.environment.tile_width)
        y = int(y // self.environment.tile_length)
        return x, y

    def screen_to_environment(self, x, y) -> (float, float):
        """
        Converts coordinates in screen coordinate-system to environment coordinate-system.
        Args:
            x: x coordinate on the screen.
            y: y coordinate on the screen.

        Returns:
            (x, y) with x, y in environment coordinate-system.
        """
        x, y, z = self.scatter.transform_inv.transform_point(x, y, 0)
        return -y, x

    def environment_to_scatter(self, x, y) -> (float, float):
        """
        Converts coordinates in environment coordinate-system to scatter coordinate-system.
        Args:
            x: x coordinate in environment.
            y: y coordinate in environment.

        Returns:
            (x, y) with x, y in scatter coordinate-system.
        """
        return y, x
