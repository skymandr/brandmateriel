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
            l.K_ESCAPE: 'quit', l.K_F1: 'help',
            }


class Game(object):
    """
    Here be docstring.
    """

    X = U = 0
    Y = V = 1
    Z = W = 2

    def __init__(self, config, world):
        self._config = config

        self.world = e.mapper.Map(world)

        self.player = e.mobs.Player(e.triDobjects.FireFighter(scale=2.0))
        self.player.position = (np.array([64.0, 64.0, 5.0]))

        self._populate_world()

        self.camera = e.camera.Camera(screen=e.camera.Screen(
            resolution=config["resolution"]))

        if config["camera"] == "rear":
            self.update_camera = self.update_rear_camera
            self.config["view"] = (self._view[0], self._view[0])
            D = self._view[self.Y] * (1 + np.sqrt(2)) * 0.5
            h = (self.camera.screen.extent[self.Y] * 0.5 -
                 self.camera.screen.position[self.Z])
            d = self.camera.distance
        else:
            self.update_camera = self.update_fixed_camera
            D = self._view[self.Y]
            h = (self.camera.screen.extent[self.Y] * 0.5 -
                 self.camera.screen.position[self.Z])
            d = self.camera.distance

        self._culling_height = np.ceil((h * (D / d + 1.0) + np.ceil(
            self.world.patch_positions[:, :, 2].max())))

        self.light_source = e.shader.LightSource()

        self.shader = e.shader.Shader(self.light_source,
                                      cutoff_distance=self._view[self.Y])

        self.update_camera()

    @property
    def config(self):
        return self._config

    @config.setter
    def config(self, val):
        self._config = val

    @property
    def focus_position(self):
        return self.player.position

    @property
    def _view(self):
        return self._config["view"]

    def update_fixed_camera(self):
        offset = np.array([0, self._view[self.Y] / 2.0 + 9.0, -0.0])

        self.camera.position = self.focus_position - offset

        self.camera.position[self.Z] = max(self.camera.position[self.Z], 6.0)

        self.light_source.position = self.camera.position + np.array([0, 0, 0])

    def update_rear_camera(self):
        look_at = self.focus_position.copy()
        look_at[self.Z] = max(look_at[self.Z], 6.0)
        offset = np.array([0, self._view[self.Y] / 2.0 + 9.0, -0.0])

        self.camera.position = look_at - offset

        self.camera.look_at_point(look_at)

        self.light_source.position = self.camera.position + np.array([0, 0, 0])

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

                elif KEYBOARD[event.key] == 'left':

                    self.player.yaw = ((self.player.yaw + np.pi / 24) %
                                       (2 * np.pi))

                elif KEYBOARD[event.key] == 'right':

                    self.player.yaw = ((self.player.yaw - np.pi / 24) %
                                       (2 * np.pi))

                elif KEYBOARD[event.key] == 'up':

                    self.player.pitch = min(self.player.pitch + np.pi / 24,
                                            np.pi * 0.5)

                elif KEYBOARD[event.key] == 'down':

                    self.player.pitch = max(self.player.pitch - np.pi / 24,
                                            -np.pi * 0.5)

                else:

                    pass
                    # flag = self._relay_input(event.key)

            elif event.type == l.MOUSEMOTION:

                motion = np.array(pygame.mouse.get_rel())

                self.player.yaw = (self.player.yaw - motion[self.X] *
                                   np.pi / 360) % (2 * np.pi)

                self.player.pitch = (self.player.pitch - motion[self.Y] *
                                     np.pi / 360)

                if self.player.pitch < -np.pi * 0.6082:

                    self.player.pitch = -np.pi * 0.6082

                elif self.player.pitch > np.pi * 0.6082:

                    self.player.pitch = np.pi * 0.6082

            elif event.type == l.MOUSEBUTTONDOWN:

                if event.button == 1:

                    self.player.fire = True

                elif event.button == 2:

                    self.player.rocket = True

                elif event.button == 3:

                    self.player.thrust = True

            elif event.type == l.MOUSEBUTTONUP:

                if event.button == 1:

                    self.player.fire = False

                elif event.button == 2:

                    self.player.rocket = False

                elif event.button == 3:

                    self.player.thrust = False

        return flag

    def do_step(self, surface):
        flag = self.handle_inputs()

        self.player.move()

        self.player.impose_boundary_conditions(self.world)

        self.update_camera()

        # get map in view:
        if self.camera.position[self.Z] < self._culling_height:
            map_positions = self.world.patch_positions_list(
                self.focus_position, self._view)
            map_normals = self.world.normals_list(self.focus_position,
                                                  self._view)
            map_patches, map_depths = self.camera.get_screen_coordinates(
                self.world.patches_list(self.focus_position, self._view))
            map_colours = self.world.colours_list(self.focus_position,
                                                  self._view)
            map_colours = self.shader.apply_lighting(map_positions,
                                                     map_normals,
                                                     map_colours,
                                                     culling=False)

        # get objects in view:
        pass

        # get player:
        player_positions = self.player.model.positions
        player_normals = self.player.model.normals
        player_patches, player_depth = self.camera.get_screen_coordinates(
            self.player.model.patches)
        player_colours = self.player.model.colours.copy()
        player_colours = self.shader.apply_lighting(player_positions,
                                                    player_normals,
                                                    player_colours)

        # aggregate object data:
        positions = np.r_[map_positions, player_positions]
        patches = list(map_patches[:])
        patches.extend(list(player_patches[:]))
        # normals = np.r_[map_normals, player_normals]
        colours = np.r_[map_colours, player_colours]

        # impose view boundaries:
        pass

        # # apply shading
        # colours = self.shader.apply_lighting(positions, normals, colours)

        # sort patches
        order = np.argsort(-((positions - self.camera.position) ** 2).mean(-1))

        # draw
        surface.fill((0, 0, 0))

        for n in order:
            if colours[n, 3]:
                pygame.draw.polygon(surface, colours[n], patches[n])

        self.handle_inputs()

        return flag
