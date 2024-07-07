from planar_robotics_configurator.model.environment import MoverPreset


class DrawMode:
    pass


class TilesMode(DrawMode):
    pass


class MoverMode(DrawMode):

    def __init__(self, preset: MoverPreset):
        self.preset = preset


class WorkingStationMode(DrawMode):
    pass
