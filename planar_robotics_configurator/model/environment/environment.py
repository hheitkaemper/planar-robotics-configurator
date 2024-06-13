from dataclasses import dataclass, field

import numpy as np


@dataclass(frozen=False)
class Environment:
    """
    Represents a planar robotics environment.
    :param name: Name of the environment. Used to identify the environment.
    :param num_width: Width number of tiles for the environment.
    :param num_length: Length number of tiles for the environment.
    :param tiles: [num_width, num_length] Array of bool. 1 for a tile at the position, 0 else
    :param tile_width: width of the tiles in the environment.
    :param tile_length: length of the tiles in the environment.
    :param table_height: height of the table in the environment.
    :param std_noise: Standard deviation of the noise in the environment.
    """
    name: str
    num_width: int = 10
    num_length: int = 10
    tiles: np.ndarray[bool] = field(init=False)
    tile_width: float = 25
    tile_length: float = 25
    table_height: float = 50
    std_noise: float = 0.5
