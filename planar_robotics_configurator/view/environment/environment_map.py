import numpy as np
from kivy.core.window import Window
from kivy.graphics import Color, Rectangle
from kivy.graphics.context_instructions import Scale
from kivy.graphics.instructions import Canvas
from kivy.graphics.transformation import Matrix
from kivy.input import MotionEvent
from kivy.uix.scatter import Scatter
from kivymd.uix.widget import MDWidget

from planar_robotics_configurator.model.environment.environment import Environment
from planar_robotics_configurator.model.environment.mover import Mover
from planar_robotics_configurator.model.environment.mover_preset import MoverPreset
from planar_robotics_configurator.view.environment.dialog import MoverSettingsDialog
from planar_robotics_configurator.view.utils.custom_snackbar import CustomSnackbar


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


class HoverRectangle(Rectangle):
    """
    Represents a rectangle for which it is possible to store the x and y position of the tile on which it hovers.
    """

    def __init__(self, x, y, **kwargs):
        super(HoverRectangle, self).__init__(**kwargs)
        self.x = x
        self.y = y


class EnvironmentMap(MDWidget):
    """
    Defines a map which can be moved by middle and right click and zoomed with scroll-wheel.
    Thous transformations are automatically applied to all canvas which are drawn to self.scatter.
    Draws the given environment.
    """

    def __init__(self):
        super().__init__()
        Window.bind(mouse_pos=self.on_mouse_over)
        self.draw_mode: str = "tiles"
        self.selected_mover_preset: MoverPreset | None = None
        self.scatter: EnvironmentScatter = EnvironmentScatter()
        self.environment: Environment | None = None
        # Kivy coordinate system to environment coordinate system
        with self.scatter.canvas.before:
            Scale(1, -1, 1)
        with self.scatter.canvas:
            self.scatter.tiles_background_canvas = Canvas()
            self.scatter.tiles_canvas = Canvas()
            self.scatter.movers_canvas = Canvas()
            self.scatter.hover_rect_color = Color(0, 0, 0, 0)
            self.scatter.hover_rect = HoverRectangle(-1, -1, pos=(0, 0), size=(1, 1))
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
        if "button" in touch.profile and touch.button == "left" and self.environment is not None:
            pos = self.screen_to_tile_position(*touch.pos)
            if 0 <= pos[0] < self.environment.num_width and 0 <= pos[1] < self.environment.num_length:
                # Edit mover if there is a mover.
                mover = next(filter((lambda m: m.x == pos[0] and m.y == pos[1]), self.environment.movers), None)
                if mover is not None:
                    MoverSettingsDialog(self, pos[0], pos[1], self.selected_mover_preset, mover).open()
                    return True
                # Place/remove tile if the draw_mode is tiles.
                if self.draw_mode == "tiles":
                    self.environment.set_tile(*pos, 1 - self.environment.get_tile(*pos))
                    self.remove_hover_rect()
                    self.redraw_tile(*pos)
                    return True
                # Place a mover if the position is on a tile.
                if self.draw_mode == "mover":
                    if self.environment.get_tile(*pos) == 0:
                        CustomSnackbar("Movers can only be placed on a tile").open()
                        return True
                    MoverSettingsDialog(self, pos[0], pos[1], self.selected_mover_preset).open()
                    return True

        return super().on_touch_down(touch)

    def on_mouse_over(self, window, pos):
        """
        Event on mouse over. Draw hover rect if mouse is over the possible area of tiles and movers.
        :param pos: position of mouse over, (x, y).
        """
        if self.environment is None:
            return
        pos = self.screen_to_tile_position(*pos)
        if not (0 <= pos[0] < self.environment.num_width and 0 <= pos[1] < self.environment.num_length):
            self.remove_hover_rect()
            return
        self.draw_hover_tile(*pos)

    def remove_hover_rect(self):
        """
        Hide the hover rect to the user. Removes the color and sets the position of the hover rect to (-1, -1)
        """
        self.scatter.hover_rect_color.a = 0
        self.scatter.hover_rect.x = -1
        self.scatter.hover_rect.y = -1

    def draw_hover_tile(self, x, y):
        """
        Draws a hover rect at position (x, y) in tile position.
        The hover rect color depends on presents of the hovered tile or mover.
        :param x: x position of the hovered tile or mover.
        :param y: y position of the hovered tile or mover.
        """
        if self.scatter.hover_rect.x == x and self.scatter.hover_rect.y == y:
            return
        self.scatter.hover_rect.x = x
        self.scatter.hover_rect.y = y
        mover = next(filter((lambda m: m.x == x and m.y == y), self.environment.movers), None)
        if mover is not None:
            self.scatter.hover_rect_color.rgba = (0, 0, 0, 0.4)
            x_pad = (1 - (mover.preset.width / self.environment.tile_width)) / 2
            y_pad = (1 - (mover.preset.length / self.environment.tile_length)) / 2
            self.scatter.hover_rect.pos = self.tile_position_to_scatter(mover.x + x_pad, mover.y + y_pad)
            self.scatter.hover_rect.size = self.environment_to_scatter(mover.preset.width, mover.preset.length)
            return
        if self.draw_mode == "tiles":
            if self.environment.get_tile(x, y) == 1:
                # Red
                self.scatter.hover_rect_color.rgba = (1, 0.45, 0.45, 1)
            else:
                # Green
                self.scatter.hover_rect_color.rgba = (0.65, 1, 0.56, 1)
            self.scatter.hover_rect.pos = self.tile_position_to_scatter(x + 0.05, y + 0.05)
            self.scatter.hover_rect.size = self.environment_to_scatter(self.environment.tile_width * 0.9,
                                                                       self.environment.tile_length * 0.9)
            return
        if self.draw_mode == "mover":
            if self.environment.get_tile(x, y) == 0:
                self.remove_hover_rect()
                return
            self.scatter.hover_rect_color.rgba = (0.65, 1, 0.56, 1)
            x_pad = (1 - (self.selected_mover_preset.width / self.environment.tile_width)) / 2
            y_pad = (1 - (self.selected_mover_preset.length / self.environment.tile_length)) / 2
            self.scatter.hover_rect.pos = self.tile_position_to_scatter(x + x_pad, y + y_pad)
            self.scatter.hover_rect.size = self.environment_to_scatter(self.selected_mover_preset.width,
                                                                       self.selected_mover_preset.length)

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
        self.center_map()
        self.remove_hover_rect()
        self.draw_tiles_background()
        self.draw_tiles()
        self.draw_movers()

    def center_map(self):
        """
        Centers the map to the center of the screen.
        """
        if self.environment is None:
            CustomSnackbar(text="Please select an environment first!").open()
            return
        x, y = self.tile_position_to_scatter(self.environment.num_width, self.environment.num_length)
        temp = self.scatter.scale
        self.scatter.scale = 1
        self.scatter.set_center_x(self.center_x + 50 - x / 2)
        self.scatter.set_center_y(self.center_y + 50 + y / 2)
        self.scale_at(np.emath.logn(1.5, temp), self.center_x, self.center_y)

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
        self.scatter.tiles_canvas.children = []
        with self.scatter.tiles_canvas:
            Color(0.49, 0.49, 0.49, 1)
            for index, value in np.ndenumerate(self.environment.tiles):
                if value == 1:
                    Rectangle(pos=self.tile_position_to_scatter(index[0] + 0.05, index[1] + 0.05),
                              size=self.environment_to_scatter(self.environment.tile_width * 0.9,
                                                               self.environment.tile_length * 0.9))
            Color(0.2, 0.2, 0.2, 1)
            for index, value in np.ndenumerate(self.environment.tiles):
                if value == 0:
                    Rectangle(pos=self.tile_position_to_scatter(index[0] + 0.05, index[1] + 0.05),
                              size=self.environment_to_scatter(self.environment.tile_width * 0.9,
                                                               self.environment.tile_length * 0.9))

    def set_movers_mode(self, preset):
        """
        Sets the place mode to movers. Mark editable or addable movers on hover and allow to place mover on tiles.
        """
        self.remove_hover_rect()
        self.draw_mode = "mover"
        self.selected_mover_preset = preset

    def set_tiles_mode(self):
        """
        Sets the place mode to tiles. Only in this mode the hovered tiles are displayed and editable.
        """
        self.remove_hover_rect()
        self.draw_mode = "tiles"
        self.selected_mover_preset = None

    def draw_movers(self) -> None:
        """
        Removes all drawn movers and redraw all movers in the current environment.
        """
        self.scatter.movers_canvas.clear()
        for mover in self.environment.movers:
            self.draw_mover(mover)

    @staticmethod
    def is_close(pos_1, pos_2, tolerance=0.01) -> bool:
        """
        Compares two positions and checks if the difference of them are below a given tolerance.
        """
        return abs(pos_1[0] - pos_2[0]) < tolerance and abs(pos_1[1] - pos_2[1]) < tolerance

    def remove_mover(self, mover: Mover) -> None:
        """
        Removes a specific mover from the map.
        :params mover: Mover which should be removed.
        """
        x_pad = (1 - (mover.preset.width / self.environment.tile_width)) / 2
        y_pad = (1 - (mover.preset.length / self.environment.tile_length)) / 2
        pos = self.tile_position_to_scatter(mover.x + x_pad, mover.y + y_pad)
        x_pad = (1 - (mover.preset.width * 0.9 / self.environment.tile_width)) / 2
        y_pad = (1 - (mover.preset.length * 0.9 / self.environment.tile_length)) / 2
        pos_2 = self.tile_position_to_scatter(mover.x + x_pad, mover.y + y_pad)
        self.scatter.movers_canvas.children[:] = \
            [c for c in self.scatter.movers_canvas.children
             if not (isinstance(c, Rectangle) and (self.is_close(c.pos, pos) or self.is_close(c.pos, pos_2)))]

    def draw_mover(self, mover: Mover) -> None:
        """
        Draws a mover.
        :params mover: Mover object which provides the position and size of the mover.
        """
        with self.scatter.movers_canvas:
            Color(0.85, 0.85, 0.85, 1)
            x_pad = (1 - (mover.preset.width / self.environment.tile_width)) / 2
            y_pad = (1 - (mover.preset.length / self.environment.tile_length)) / 2
            Rectangle(pos=self.tile_position_to_scatter(mover.x + x_pad, mover.y + y_pad),
                      size=self.environment_to_scatter(mover.preset.width, mover.preset.length))
            Color(0.98, 1, 0.87, 1)
            x_pad = (1 - (mover.preset.width * 0.9 / self.environment.tile_width)) / 2
            y_pad = (1 - (mover.preset.length * 0.9 / self.environment.tile_length)) / 2
            Rectangle(pos=self.tile_position_to_scatter(mover.x + x_pad, mover.y + y_pad),
                      size=self.environment_to_scatter(mover.preset.width * 0.9, mover.preset.length * 0.9))

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
        x, y = self.scatter.to_local(x, y)
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
