from dataclasses import dataclass


@dataclass(frozen=False)
class MoverPreset:
    """
    Represents a preset for Mover which can be used to create a Mover
    :param width: Width (cm) of the mover.
    :param length: Length (cm) of the mover.
    :param height: Height (cm) of the mover.
    :param mass: Mass (kg) of the mover.
    """
    name: str
    width: float
    length: float
    height: float
    mass: float
