import numpy as np
from kivy.core.image import Image
from kivy.core.text import Label as CoreLabel
from kivy.core.window import Window
from kivy.graphics import Color, Rectangle, Line
from kivy.graphics.context_instructions import Scale
from kivy.graphics.instructions import Canvas
from kivy.graphics.texture import Texture
from kivy.graphics.transformation import Matrix
from kivy.input import MotionEvent
from kivy.uix.scatter import Scatter
from kivymd.uix.widget import MDWidget

from planar_robotics_configurator.model.environment import Environment, Mover, BoxCollisionShape, CircleCollisionShape
from planar_robotics_configurator.model.environment.object import Object
from planar_robotics_configurator.model.environment.working_station import WorkingStation
from planar_robotics_configurator.view.environment.dialog import (MoverSettingsDialog, WorkingStationSettings,
                                                                  ObjectSettings)
from planar_robotics_configurator.view.environment.draw_mode import (DrawMode, TilesMode, MoverMode,
                                                                     WorkingStationMode, ObjectMode)
from planar_robotics_configurator.view.utils import CustomSnackbar


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


class CollisionLine(Line):
    """
    Represents a line for which it is possible to store the mover.
    """

    def __init__(self, mover, **kwargs):
        super(CollisionLine, self).__init__(**kwargs)
        self.mover = mover


class LabelRectangle(Rectangle):
    """
    Creates a text with the center at the given position.
    The size specifies the height of the text field. The width is automatically calculated to fit the height.
    """

    def __init__(self, text: str, size, pos, **kwargs):
        self.x = pos[0]
        self.y = pos[1]
        label = CoreLabel(text=text, font_size=100)
        label.refresh()
        label.texture.flip_vertical()
        size = (size * label.texture.size[0] / label.texture.size[1], size)
        super(LabelRectangle, self).__init__(texture=label.texture, size=size,
                                             pos=(pos[0] - size[0] / 2, pos[1] - size[1] / 2), **kwargs)


class EnvironmentMap(MDWidget):
    """
    Defines a map which can be moved by middle and right click and zoomed with scroll-wheel.
    Thous transformations are automatically applied to all canvas which are drawn to self.scatter.
    Draws the given environment.
    """

    def __init__(self):
        super().__init__()
        Window.bind(mouse_pos=self.on_mouse_over)
        self.draw_mode: DrawMode = TilesMode()
        self.scatter: EnvironmentScatter = EnvironmentScatter()
        self.environment: Environment | None = None
        self.robot_texture: Texture = Image("assets/robot.png").texture
        self.robot_texture.flip_vertical()
        self.object_texture: Texture = Image("assets/cube-outline.png").texture
        self.object_texture.flip_vertical()
        self.hiding_settings = {
            "environment_background": True,
            "tiles": True,
            "movers": True,
            "movers_collision": False,
            "working_stations": True,
            "working_stations_name": True,
            "objects": True,
            "objects_name": True
        }
        # Kivy coordinate system to environment coordinate system
        with self.scatter.canvas.before:
            Scale(1, -1, 1)
        with self.scatter.canvas:
            self.scatter.tiles_background_canvas = Canvas()
            self.scatter.tiles_canvas = Canvas()
            self.scatter.movers_canvas = Canvas()
            self.scatter.movers_collision_canvas = Canvas()
            self.scatter.hover_rect_color = Color(0, 0, 0, 0)
            self.scatter.hover_rect = HoverRectangle(-1, -1, pos=(0, 0), size=(1, 1))
            self.scatter.working_stations_canvas = Canvas()
            self.scatter.objects_canvas = Canvas()
            self.scatter.texture_hover_rect_color = Color(0, 0, 0, 0)
            self.scatter.texture_hover_rect = Rectangle(texture=self.robot_texture, pos=(0, 0), size=(0, 0))
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

            if isinstance(self.draw_mode, WorkingStationMode):
                pos = self.screen_to_environment(*touch.pos)
                working_station = next(filter(
                    lambda w: self.is_close(pos, (w.position[0], w.position[1]), tolerance=0.1),
                    self.environment.working_stations), None)
                if working_station is not None:
                    WorkingStationSettings(self, working_station=working_station).open()
                    return True
                WorkingStationSettings(self, x=round(pos[0], 2), y=round(pos[1], 2)).open()
                return True
            if isinstance(self.draw_mode, ObjectMode):
                pos = self.screen_to_environment(*touch.pos)
                object_instance = next(filter(lambda o: self.is_close(pos, (o.position[0], o.position[1]),
                                                                      tolerance=0.1), self.environment.objects), None)
                if object_instance is not None:
                    ObjectSettings(self, object_instance=object_instance).open()
                    return True
                ObjectSettings(self, x=round(pos[0], 2), y=round(pos[1], 2)).open()
                return True
            pos = self.screen_to_tile_position(*touch.pos)
            if 0 <= pos[0] < self.environment.num_width and 0 <= pos[1] < self.environment.num_length:
                # Edit mover if there is a mover.
                mover = next(filter((lambda m: m.x == pos[0] and m.y == pos[1]), self.environment.movers), None)
                if mover is not None:
                    MoverSettingsDialog(self, pos[0], pos[1], None, mover).open()
                    return True
                # Place/remove tile if the draw_mode is tiles.
                if isinstance(self.draw_mode, TilesMode):
                    self.environment.set_tile(*pos, 1 - self.environment.get_tile(*pos))
                    self.remove_hover_rect()
                    self.redraw_tile(*pos)
                    return True
                # Place a mover if the position is on a tile.
                if isinstance(self.draw_mode, MoverMode):
                    if self.environment.get_tile(*pos) == 0:
                        CustomSnackbar("Movers can only be placed on a tile").open()
                        return True
                    MoverSettingsDialog(self, pos[0], pos[1], self.draw_mode.preset).open()
                    return True

        return super().on_touch_down(touch)

    def on_mouse_over(self, window, pos):
        """
        Event on mouse over. Draw hover rect if mouse is over the possible area of tiles and movers.
        :param pos: position of mouse over, (x, y).
        """
        if self.environment is None:
            return
        if isinstance(self.draw_mode, WorkingStationMode) or isinstance(self.draw_mode, ObjectMode):
            self.draw_texture_hover_rect(*self.screen_to_environment(*pos))
            return
        else:
            self.remove_texture_hover_rect()

        pos = self.screen_to_tile_position(*pos)
        if 0 <= pos[0] < self.environment.num_width and 0 <= pos[1] < self.environment.num_length:
            self.draw_hover_tile(*pos)
            return
        else:
            self.remove_hover_rect()

    def remove_hover_rect(self):
        """
        Hide the hover rect to the user. Removes the color and sets the position of the hover rect to (-1, -1)
        """
        self.scatter.hover_rect_color.a = 0
        self.scatter.hover_rect.x = -1
        self.scatter.hover_rect.y = -1

    def remove_texture_hover_rect(self):
        """
        Hide the hover robot to the user. Removes the color.
        """
        self.scatter.texture_hover_rect_color.a = 0

    def draw_texture_hover_rect(self, x, y):
        """
        Draws a texture hover rect at position (x, y) in environment position.
        :param x: x position in environment coordinate system.
        :param y: y position in environment coordinate system.
        """
        if isinstance(self.draw_mode, WorkingStationMode):
            working_station = next(filter(lambda w: self.is_close((x, y), (w.position[0], w.position[1]),
                                                                  tolerance=0.1), self.environment.working_stations),
                                   None)
            self.scatter.texture_hover_rect.texture = self.robot_texture
            if working_station is not None:
                self.scatter.texture_hover_rect_color.rgba = (0, 0, 0, 0.6)
                self.scatter.texture_hover_rect.pos = self.environment_to_scatter(working_station.position[0] - 0.1,
                                                                                  working_station.position[1] - 0.1)
                self.scatter.texture_hover_rect.size = self.environment_to_scatter(0.2, 0.2)
                return
        if isinstance(self.draw_mode, ObjectMode):
            object_instance = next(filter(lambda o: self.is_close((x, y), (o.position[0], o.position[1]),
                                                                  tolerance=0.1), self.environment.objects),
                                   None)
            self.scatter.texture_hover_rect.texture = self.object_texture
            if object_instance is not None:
                self.scatter.texture_hover_rect_color.rgba = (0, 0, 0, 0.6)
                self.scatter.texture_hover_rect.pos = self.environment_to_scatter(object_instance.position[0] - 0.1,
                                                                                  object_instance.position[1] - 0.1)
                self.scatter.texture_hover_rect.size = self.environment_to_scatter(0.2, 0.2)
                return
        self.scatter.texture_hover_rect_color.rgba = (1, 1, 1, 1)
        self.scatter.texture_hover_rect.pos = self.environment_to_scatter(x - 0.1, y - 0.1)
        self.scatter.texture_hover_rect.size = self.environment_to_scatter(0.2, 0.2)

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
        if isinstance(self.draw_mode, TilesMode):
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
        if isinstance(self.draw_mode, MoverMode):
            if self.environment.get_tile(x, y) == 0:
                self.remove_hover_rect()
                return
            self.scatter.hover_rect_color.rgba = (0.65, 1, 0.56, 1)
            preset = self.draw_mode.preset
            x_pad = (1 - (preset.width / self.environment.tile_width)) / 2
            y_pad = (1 - (preset.length / self.environment.tile_length)) / 2
            self.scatter.hover_rect.pos = self.tile_position_to_scatter(x + x_pad, y + y_pad)
            self.scatter.hover_rect.size = self.environment_to_scatter(preset.width, preset.length)

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
        self.redraw()

    def reset(self):
        """
        Resets the environment to None.
        """
        self.environment = None
        self.remove_hover_rect()
        self.remove_texture_hover_rect()
        self.scatter.tiles_background_canvas.clear()
        self.scatter.tiles_canvas.children = []
        self.scatter.movers_canvas.clear()
        self.scatter.movers_collision_canvas.clear()
        self.scatter.working_stations_canvas.clear()
        self.scatter.objects_canvas.clear()

    def redraw(self):
        """
        Redraws the environment.
        """
        if self.environment is None:
            return
        self.remove_hover_rect()
        self.remove_texture_hover_rect()
        self.draw_tiles_background()
        self.draw_tiles()
        self.draw_movers()
        self.draw_working_stations()
        self.draw_objects()

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
        if not self.hiding_settings["environment_background"]:
            return
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
        if not self.hiding_settings["tiles"]:
            return
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
        if not self.hiding_settings["tiles"]:
            return
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
        self.remove_texture_hover_rect()
        self.draw_mode = MoverMode(preset)

    def set_tiles_mode(self):
        """
        Sets the place mode to tiles. Only in this mode the hovered tiles are displayed and editable.
        """
        self.remove_hover_rect()
        self.remove_texture_hover_rect()
        self.draw_mode = TilesMode()

    def set_working_station_mode(self):
        """
        Sets the place mode to working stations.
        """
        self.remove_hover_rect()
        self.remove_texture_hover_rect()
        self.draw_mode = WorkingStationMode()

    def set_object_mode(self):
        """
        Sets the place mode to objects.
        """
        self.remove_hover_rect()
        self.remove_texture_hover_rect()
        self.draw_mode = ObjectMode()

    def draw_movers(self) -> None:
        """
        Removes all drawn movers and redraw all movers in the current environment.
        """
        self.scatter.movers_canvas.clear()
        self.scatter.movers_collision_canvas.clear()
        for mover in self.environment.movers:
            self.draw_mover(mover)

    def draw_working_stations(self) -> None:
        """
        Removes all drawn working stations and redraw all working stations in the current environment.
        """
        self.scatter.working_stations_canvas.clear()
        for working_station in self.environment.working_stations:
            self.draw_working_station(working_station)

    def draw_objects(self) -> None:
        """
        Removes all drawn objects and redraw all objects in the current environment.
        """
        self.scatter.objects_canvas.clear()
        for object_instance in self.environment.objects:
            self.draw_object(object_instance)

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

        self.scatter.movers_collision_canvas.children[:] = \
            [c for c in self.scatter.movers_collision_canvas.children
             if not (isinstance(c, CollisionLine) and c.mover == mover)]

    def draw_mover(self, mover: Mover) -> None:
        """
        Draws a mover.
        :params mover: Mover object which provides the position and size of the mover.
        """
        if not self.hiding_settings["movers"]:
            return
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
        if self.hiding_settings["movers_collision"]:
            with self.scatter.movers_collision_canvas:
                center_pos = self.tile_position_to_environment(mover.x + 0.5, mover.y + 0.5)
                if isinstance(mover.collision_shape, CircleCollisionShape):
                    pos = self.environment_to_scatter(center_pos[0] - mover.collision_shape.radius,
                                                      center_pos[1] - mover.collision_shape.radius)
                    size = self.environment_to_scatter(mover.collision_shape.radius * 2,
                                                       mover.collision_shape.radius * 2)
                    Color(1, 0, 0, 1)
                    CollisionLine(mover, ellipse=(pos[0], pos[1], size[0], size[1]))
                if isinstance(mover.collision_shape, BoxCollisionShape):
                    pos = self.environment_to_scatter(center_pos[0] - mover.collision_shape.width / 2,
                                                      center_pos[1] - mover.collision_shape.length / 2)
                    size = self.environment_to_scatter(mover.collision_shape.width, mover.collision_shape.length)
                    Color(1, 0, 0, 1)
                    CollisionLine(mover, rectangle=(pos[0], pos[1], size[0], size[1]))

    def draw_working_station(self, working_station: WorkingStation) -> None:
        """
        Draws a working station.
        :params working_station: WorkingStation object which should be drawn.
        """
        if not self.hiding_settings["working_stations"]:
            return
        with self.scatter.working_stations_canvas:
            if self.hiding_settings["working_stations_name"]:
                Color(1, 1, 1, 1)
                LabelRectangle(text=working_station.name, size=self.environment_to_scatter(0.1, 0.1)[0],
                               pos=self.environment_to_scatter(working_station.position[0] + 0.15,
                                                               working_station.position[1]))
            Color(working_station.color[0], working_station.color[1], working_station.color[2],
                  working_station.color[3])
            Rectangle(
                texture=self.robot_texture,
                pos=self.environment_to_scatter(working_station.position[0] - 0.1, working_station.position[1] - 0.1),
                size=self.environment_to_scatter(0.2, 0.2))

    def remove_working_station(self, working_station: WorkingStation) -> None:
        """
        Removes a specific working station from the map.
        :params working_station: WorkingStation which should be removed.
        """
        pos = self.environment_to_scatter(working_station.position[0] - 0.1, working_station.position[1] - 0.1)
        pos2 = self.environment_to_scatter(working_station.position[0] + 0.15, working_station.position[1])
        self.scatter.working_stations_canvas.children[:] = \
            [c for c in self.scatter.working_stations_canvas.children
             if not (isinstance(c, Rectangle) and (self.is_close(c.pos, pos)))
             and not (isinstance(c, LabelRectangle) and self.is_close((c.x, c.y), pos2))]

    def draw_object(self, object_instance: Object) -> None:
        """
        Draws a working station.
        :params working_station: WorkingStation object which should be drawn.
        """
        if not self.hiding_settings["objects"]:
            return
        with self.scatter.objects_canvas:
            if self.hiding_settings["objects_name"]:
                Color(1, 1, 1, 1)
                LabelRectangle(text=object_instance.name, size=self.environment_to_scatter(0.1, 0.1)[0],
                               pos=self.environment_to_scatter(object_instance.position[0] + 0.15,
                                                               object_instance.position[1]))
            Color(object_instance.color[0], object_instance.color[1], object_instance.color[2],
                  object_instance.color[3])
            Rectangle(
                texture=self.object_texture,
                pos=self.environment_to_scatter(object_instance.position[0] - 0.1, object_instance.position[1] - 0.1),
                size=self.environment_to_scatter(0.2, 0.2))

    def remove_object(self, object_instance: Object) -> None:
        """
        Removes a specific working station from the map.
        :params working_station: WorkingStation which should be removed.
        """
        pos = self.environment_to_scatter(object_instance.position[0] - 0.1, object_instance.position[1] - 0.1)
        pos2 = self.environment_to_scatter(object_instance.position[0] + 0.15, object_instance.position[1])
        self.scatter.objects_canvas.children[:] = \
            [c for c in self.scatter.objects_canvas.children
             if not (isinstance(c, Rectangle) and (self.is_close(c.pos, pos)))
             and not (isinstance(c, LabelRectangle) and self.is_close((c.x, c.y), pos2))]

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
        return self.environment_to_scatter(x, y)

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
        return -y / 100, x / 100

    def environment_to_scatter(self, x, y) -> (float, float):
        """
        Converts coordinates in environment coordinate-system to scatter coordinate-system.
        Args:
            x: x coordinate in environment.
            y: y coordinate in environment.

        Returns:
            (x, y) with x, y in scatter coordinate-system.
        """
        return y * 100, x * 100
