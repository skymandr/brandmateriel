import numpy as np
import pygame as pg
from pygame import locals as l
import engine as e

KEYBOARD = {l.K_UP: 'up', l.K_k: 'up', l.K_w: 'up',
            l.K_DOWN: 'down', l.K_j: 'down', l.K_s: 'down',
            l.K_LEFT: 'left', l.K_h: 'left', l.K_a: 'left',
            l.K_RIGHT: 'right', l.K_l: 'right', l.K_d: 'right',
            l.K_RETURN: 'start', l.K_SPACE: 'start',
            l.K_ESCAPE: 'quit', l.K_F1: 'help'}


class Game(object):
    """
    Here be docstring.
    """

    X = U = 0
    Y = V = 1
    Z = W = 2

    def __init__(self, config):
        self._config = config

        self._populate_world()

    @property
    def _position(self):
        return None

    @property
    def _view(self):
        return self._config["view"]

    @property
    def map_view(self):
        position = np.round(self._position).astype(np.int)
        view = self._view
        X, Y = np.mgrid[position[self.Y] - view[self.Y] / 2 - 1:
                        position[self.Y] + view[self.Y] / 2 + 1,
                        position[self.X] - view[self.X] / 2 - 1:
                        position[self.X] + view[self.X] / 2 + 1]
        X, Y = X % self.world.shape[self.X], Y % self.world.shape[self.Y]

        return self.world.positions_array[(Y, X), :]

    def _populate_world(self):
        pass
