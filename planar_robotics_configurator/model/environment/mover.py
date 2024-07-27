from dataclasses import dataclass

from planar_robotics_configurator.model.environment.mover_preset import MoverPreset


@dataclass(frozen=False)
class Mover:
    """
    Represents a planar robot.
    :param preset: Preset of the planar robot which provides size and mass of the robot.
    :param x: x Position of the planar robot in the tiles coordinate system.
    :param y: y Position of the planar robot in the tiles coordinate system.
    :param collision_shape: Collision shape of the planar robot in the tiles coordinate system. Can be an empty list,
        a list with one element for a circular shape and a list with two elements for a box shape.
    """
    preset: MoverPreset
    x: int
    y: int
    collision_shape: list[float]

    def to_config(self):
        config = {
            "x": self.x,
            "y": self.y,
            "width": self.preset.width,
            "length": self.preset.length,
            "height": self.preset.height,
            "mass": self.preset.mass
        }
        return config
