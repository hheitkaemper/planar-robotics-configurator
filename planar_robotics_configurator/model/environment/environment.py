from dataclasses import dataclass, field
import numpy as np


@dataclass(frozen=False)
class Environment:
    """
    Represents a planar robotics environment.
    :param name: Name of the environment. Used to identify the environment.
    :param num_width: Width number of tiles for the environment in x direction.
    :param num_length: Length number of tiles for the environment in y direction.
    :param tiles: [num_width, num_length] Array of int. 1 for a tile at the position, 0 else
    :param tile_width: width (cm) of the tiles in the environment in x direction.
    :param tile_length: length (cm) of the tiles in the environment in y direction.
    :param table_height: height of the table in the environment.
    :param std_noise: Standard deviation of the noise in the environment.
    """
    name: str
    num_width: int = 10
    num_length: int = 10
    tiles: np.ndarray[int] = field(init=False)
    tile_width: float = 25
    tile_length: float = 25
    table_height: float = 50
    std_noise: float = 0.5

    def __post_init__(self):
        self.init_tiles()

    def init_tiles(self):
        """
        Creates the tiles of the environment.
        Sets all tiles to zero, which represents a not existing tile.
        """
        self.tiles = np.zeros((self.num_width, self.num_length), dtype=int)

    def get_tile(self, x, y) -> bool:
        """
        Gets a tile at position x, y in the tile coordinate-system.
        :param x: x coordinate of the tile.
        :param y: y coordinate of the tile.
        """
        return self.tiles[x, y]

    def set_tile(self, x, y, value):
        """
        Sets the value of a tile at position x, y in the tile coordinate-system.
        :param x: x coordinate of the tile.
        :param y: y coordinate of the tile.
        :param value: value of the tile, this value should only be 0 for not existing and 1 for existing tile.
        """
        assert value in [0, 1]
        self.tiles[x, y] = value
