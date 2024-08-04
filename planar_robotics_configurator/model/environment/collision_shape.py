from dataclasses import dataclass


@dataclass(frozen=False)
class CollisionShape:
    """
    Represents the collision shape of a mover.
    Abstract base class for all collision shapes.
    """

    def to_config(self):
        raise NotImplementedError()

    @staticmethod
    def from_config(config):
        raise NotImplementedError()


@dataclass(frozen=False)
class CircleCollisionShape(CollisionShape):
    """
    Represents the collision shape of a circle.
    """
    radius: float

    def to_config(self):
        config = {
            "shape": "circle",
            "radius": self.radius
        }
        return config

    @staticmethod
    def from_config(config):
        return CircleCollisionShape(
            radius=config["radius"]
        )


@dataclass(frozen=False)
class BoxCollisionShape(CollisionShape):
    """
    Represents the collision shape of a box.
    """
    width: float
    length: float

    def to_config(self):
        config = {
            "shape": "box",
            "width": self.width,
            "length": self.length
        }
        return config

    @staticmethod
    def from_config(config):
        return BoxCollisionShape(
            width=config["width"],
            length=config["length"]
        )
