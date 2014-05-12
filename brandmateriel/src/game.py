# TODO:
# A lot of things can be stolen from pygame_demo.py, but implemented in better
# ways...
import numpy as np
import pygame
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

        self.map = e.mapper.Map()

        self.player = e.mobs.Movable(e.triDobjects.FireFighter())

        self._populate_world()

        self.camera = e.camera.Camera()

        if config["camera"] == "rear":
            self.update_camera = self.update_rear_camera
        else:
            self.update_camera = self.update_fixed_camera

    @property
    def focus_position(self):
        return self.player.position

    @property
    def _view(self):
        return self._config["view"]

    def update_fixed_camera(self):
        offset = np.array([0, self._view[self.Y] / 2.0 + 9.0,
                           max(self.focus_position[self.Z], 6.0)])

        self.camera.position = self.focus_position - offset

    def update_rear_camera(self):
        look_at = self.focus_position.copy()
        look_at[self.Z] = max(look_at[self.Z], 6.0)
        offset = np.array([0, self._view[self.Y] / 2.0 + 9.0, look_at[self.Z]])

        self.camera.position = self.focus_position - offset

        self.camera.look_at(look_at)

    def _populate_world(self):
        pass

    def close_game(self):
        """ Close game. """

        return "quit"

    def return_to_menu(self):
        """ Close game. """

        return "menu"

    def handle_inputs(self):
        """ Should later handle inputs from user. """
        flag = "game"

        for event in pygame.event.get():

            if event.type == l.QUIT:

                flag = self.close_game()

            elif event.type == l.KEYDOWN and event.key in KEYBOARD.keys():

                if KEYBOARD[event.key] == 'quit':

                    flag = self.return_to_menu()

                elif KEYBOARD[event.key] == 'up':

                    self.player.pitch = min(self.player.pitch + np.pi / 24,
                                            np.pi / 2)

                elif KEYBOARD[event.key] == 'down':

                    self.player.pitch = max(self.player.pitch - np.pi / 24,
                                            -np.pi / 2)

                elif KEYBOARD[event.key] == 'left':

                    self.player.yaw = ((self.player.yaw + np.pi / 24) %
                                       2 * np.pi)

                elif KEYBOARD[event.key] == 'right':

                    self.player.yaw = ((self.player.yaw - np.pi / 24) %
                                       2 * np.pi)

                else:

                    pass
                    # flag = self._relay_input(event.key)

        return flag
        pass

    def do_step(self):
        self.handle_inputs()

        self.player.move()

        self.player.impose_boundary_conditions()

        self.update_camera()

        # get view
        # impose view boundaries
        # sort patches
        # get camerapositions
        # draw

        return "game"
