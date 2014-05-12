# TODO:
# A lot of things can be stolen from pygame_demo.py, but implemented in better
# ways...
import numpy as np
import pygame as pg
from pygame import locals as l
import engine as e
from .assets import triD

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

        self.map = e.mapper.Map()

        self.player = e.mobs.Movable()

        self._populate_world()

    @property
    def _position(self):
        return None

    @property
    def _view(self):
        return self._config["view"]

    def _populate_world(self):
        pass
