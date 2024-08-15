import random
import string
from dataclasses import dataclass

from planar_robotics_configurator.model.environment.collision_shape import CollisionShape, BoxCollisionShape, \
    CircleCollisionShape
from planar_robotics_configurator.model.environment.mover_preset import MoverPreset


@dataclass(frozen=False)
class Mover:
    """
    Represents a planar robot.
    :param preset: Preset of the planar robot which provides size and mass of the robot.
    :param x: x Position of the planar robot in the tiles coordinate system.
    :param y: y Position of the planar robot in the tiles coordinate system.
    :param collision_shape: Collision shape of the planar robot.
    """
    preset: MoverPreset
    x: int
    y: int
    collision_shape: CollisionShape | None

    def to_config(self, tile_width, tile_length):
        config = {
            "x": (self.x + 0.5) * tile_width,
            "y": (self.y + 0.5) * tile_length,
            "width": self.preset.width / 2,
            "length": self.preset.length / 2,
            "height": self.preset.height / 2,
            "mass": self.preset.mass,
            "collision_shape": self.collision_shape.to_config() if self.collision_shape is not None else None
        }
        return config

    @staticmethod
    def from_config(config, tile_width, tile_length):
        from planar_robotics_configurator.model.configurator_model import ConfiguratorModel
        width = config["width"] * 2
        length = config["length"] * 2
        height = config["height"] * 2
        mass = config["mass"]
        presets = list(filter(lambda p: p.width == width and p.length == length and p.height == height
                                        and p.mass == mass, ConfiguratorModel().mover_presets))
        if len(presets) == 0:
            preset = MoverPreset(name=''.join(random.choice(string.ascii_uppercase + string.digits) for _ in range(10)),
                                 width=width, length=length, height=height, mass=mass)
            ConfiguratorModel().mover_presets.append(preset)
        else:
            preset = presets[0]
        collision_shape_config = config["collision_shape"]
        collision_shape = None
        match collision_shape_config["shape"]:
            case "box":
                collision_shape = BoxCollisionShape.from_config(collision_shape_config)
            case "circle":
                collision_shape = CircleCollisionShape.from_config(collision_shape_config)
        return Mover(
            preset=preset,
            x=round((config["x"] / tile_width) - 0.5, 0),
            y=round((config["y"] / tile_length) - 0.5, 0),
            collision_shape=collision_shape
        )
