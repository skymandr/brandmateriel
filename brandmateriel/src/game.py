import numpy as np
import pygame
from pygame import locals as l
import engine as e

KEYBOARD = {l.K_UP: 'up', l.K_k: 'up', l.K_w: 'up',
            l.K_DOWN: 'down', l.K_j: 'down', l.K_s: 'down',
            l.K_LEFT: 'left', l.K_h: 'left', l.K_a: 'left',
            l.K_RIGHT: 'right', l.K_l: 'right', l.K_d: 'right',
            l.K_RETURN: 'start', l.K_SPACE: 'start',
            l.K_ESCAPE: 'quit', l.K_F1: 'help', l.K_TAB: 'pause'
            }


class Game(object):
    """
    Here be docstring.
    """

    X = U = 0
    Y = V = 1
    Z = W = 2

    def __init__(self, config, world, font, fontsize):
        self._config = config

        print "initialising world map ... ",
        self.world = e.mapper.Map(world)
        print "DONE"

        print "loading fonts ... ",
        fontsize *= config["resolution"][0] / 320
        self._font = pygame.font.Font(font, fontsize)
        print "DONE"

        print "loading game objects ... ",
        if not self._config[" "]:
            self.player = e.mobs.Player(e.triDobjects.FireFighter(scale=2.0))
            # self.player = e.mobs.Player(e.triDobjects.Pika(scale=3.0))
        else:
            self.player = e.mobs.Player(e.triDobjects.Lander(scale=1.0))

        self.player.position = (np.array([64.0, 64.0, 5.0]))
        print "DONE"

        print "initialising game objects ... ",
        self._populate_world()
        self.shots = e.particles.Shots()
        self.shrapnel = e.particles.Shrapnel()
        self.exhaust = e.particles.Exhaust()
        print "DONE"

        print "seting up camera ... ",
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
            self.world.patch_positions[:, :, self.Z].max())))

        self.light_source = e.shader.LightSource()

        self.shader = e.shader.Shader(self.light_source,
                                      cutoff_distance=self._view[self.Y] * 0.5
                                      + self.camera.distance,
                                      linear_distance=self._view[self.Y] *
                                      0.75)

        self.update_camera()
        print "DONE"

        pygame.event.set_grab(True)
        pygame.mouse.set_visible(False)

        self._pause = False
        print "game starting"

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
        offset = self._view[self.Y] / 2.0 + 9.0

        self.camera.position = (look_at - offset *
                                np.array([-np.sin(self.player.model.yaw),
                                          np.cos(self.player.model.yaw), 0.0]))

        self.camera.look_at_point(look_at)

        self.light_source.position = self.camera.position + np.array([0, 0, 0])

    def _populate_world(self):
        n_houses = 16
        settlements = []
        angles = 2 * np.pi * np.random.random(n_houses)
        candidates = self.world.map_positions.copy()

        for n in xrange(n_houses):
            x, y = (np.random.random(2) * self.world.shape).astype(np.int)
            X, Y = np.mgrid[x - 1: x + 2, y - 1: y + 2]
            X %= self.world.shape[self.X]
            Y %= self.world.shape[self.Y]

            while((candidates[X, Y, self.Z] < 0).any()):
                x, y = (np.random.random(2) * self.world.shape).astype(np.int)
                X, Y = np.mgrid[x - 1: x + 2, y - 1: y + 2]
                X %= self.world.shape[self.X]
                Y %= self.world.shape[self.Y]

            settlements.append(e.triDobjects.House(
                position=np.array([x, y, candidates[x, y, self.Z]]),
                yaw=angles[n]))

            candidates[X, Y, self.Z] *= 0

        self.houses = settlements

    def close_game(self):
        """ Close game. """

        return "quit"

    def return_to_menu(self):
        """ Close game. """

        return "menu"

    def handle_inputs(self):
        """ Handles inputs from user. """
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

                elif KEYBOARD[event.key] == 'pause':

                    self._pause = not self._pause

                    pygame.event.set_grab(not self._pause)

                    pygame.mouse.set_visible(self._pause)

                    pygame.mouse.get_rel()

                else:

                    pass
                    # flag = self._relay_input(event.key)

            elif event.type == l.MOUSEMOTION and pygame.event.get_grab():

                motion = np.array(pygame.mouse.get_rel())

                self.player.yaw = (self.player.yaw - motion[self.X] *
                                   np.pi / 360) % (2 * np.pi)

                self.player.pitch = (self.player.pitch - motion[self.Y] *
                                     np.pi / 360)

                if self.player.pitch < -2.0 * np.pi / 3.0:

                    self.player.pitch = -2.0 * np.pi / 3.0

                elif self.player.pitch > 3.0 * np.pi / 4.0:

                    self.player.pitch = 3.0 * np.pi / 4.0

            elif event.type == l.MOUSEBUTTONDOWN:

                if pygame.event.get_grab():

                    if event.button == 1:

                        self.player.fire = True

                    elif event.button == 2:

                        self.player.rocket = True

                    elif event.button == 3:

                        self.player.thrust = True

                else:

                    pygame.event.set_grab(True)

                    pygame.mouse.set_visible(False)

                    pygame.mouse.get_rel()

            elif event.type == l.MOUSEBUTTONUP:

                if event.button == 1:

                    self.player.fire = False

                elif event.button == 2:

                    self.player.rocket = False

                elif event.button == 3:

                    self.player.thrust = False

        return flag

    def draw_patches(self, positions, patches, colours, surface):
        # draw objects and particles:
        order = np.argsort(-((positions - self.camera.position) ** 2).mean(-1))

        for n in order:
            if colours[n, 3]:
                pygame.draw.polygon(surface, colours[n], patches[n])
                pygame.draw.polygon(surface, colours[n], patches[n], 1)

    def do_step(self, surface):
        flag = self.handle_inputs()

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
        else:
            map_positions = np.empty((0, 3))
            map_normals = np.empty((0, 3))
            map_patches = np.empty((0, 4, 2))
            map_colours = np.empty((0, 4))

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
        # get shadow:
        if self.camera.position[self.Z] < self._culling_height:
            player_shadow, player_shadow_positions = e.shadow.get_shadows(
                self.player.model.patches.copy(), self.world)
            player_shadow, shadow_depths = self.camera.get_screen_coordinates(
                player_shadow)
            player_shadow_colours = np.array([[0, 0, 0, 1]]) * np.ones(
                (player_shadow.shape[0], 1))
        else:
            player_shadow_positions = np.empty((0, 3))
            player_shadow = np.empty((0, 4, 2))
            player_shadow_colours = np.empty((0, 4))

        # Handle particles:
        if self.player.fire and (self.shots.number == 0 or
                                 self.shots.ages[-1] > self.player.cool_down):
            self.shots.add_particle(self.player.model.gun,
                                    self.player.model.orientation[self.V] * 16
                                    + self.player.velocity, np.zeros(3))

        if self.player.thrust:
            self.exhaust.add_particle(
                self.player.model.engine,
                -self.player.model.orientation[self.W] * 8 +
                (2 * np.random.random() - 1) * 2 *
                self.player.model.orientation[self.U] +
                (2 * np.random.random() - 1) * 2 *
                self.player.model.orientation[self.V] +
                + self.player.velocity, np.zeros(3))

        if self.shots.number:
            view = self._view + self.camera.distance
            shots_positions = self.shots.patches_positions.copy()
            shots_positions = self.world.fix_view(self.focus_position, view,
                                                  shots_positions)
            shots_in_view = self.world.positions_in_view(self.focus_position,
                                                         view, shots_positions)

            if shots_in_view.size:
                shots_positions = shots_positions[shots_in_view]
                shots_patches = self.world.fix_view(
                    self.focus_position, view,
                    self.shots.patches[shots_in_view])

                if self.camera.position[self.Z] < self._culling_height:
                    shots_shadows, shots_shadow_positions = \
                        e.shadow.get_shadows(shots_patches.copy(),
                                             self.world)
                    shots_shadows, shadow_depths = \
                        self.camera.get_screen_coordinates(shots_shadows)
                    shots_shadow_colours = np.array([[0, 0, 0, 1]]) * np.ones(
                        (shots_shadows.shape[0], 1))

                else:
                    shots_shadow_positions = np.empty((0, 3))
                    shots_shadows = np.empty((0, 4, 2))
                    shots_shadow_colours = np.empty((0, 4))

                (shots_patches, shots_depths) = \
                    self.camera.get_screen_coordinates(shots_patches)
                shots_colours = self.shots.patches_colours[shots_in_view]
                shots_colours = self.shader.apply_lighting(shots_positions,
                                                           shots_positions,
                                                           shots_colours,
                                                           scatter=False)

            else:
                shots_positions = np.empty((0, 3))
                shots_patches = np.empty((0, 3, 2))
                shots_colours = np.empty((0, 4))

                shots_shadow_positions = np.empty((0, 3))
                shots_shadows = np.empty((0, 4, 2))
                shots_shadow_colours = np.empty((0, 4))

        else:
            shots_positions = np.empty((0, 3))
            shots_patches = np.empty((0, 3, 2))
            shots_colours = np.empty((0, 4))

            shots_shadow_positions = np.empty((0, 3))
            shots_shadows = np.empty((0, 4, 2))
            shots_shadow_colours = np.empty((0, 4))

        if self.exhaust.number:
            view = self._view
            exhaust_positions = self.exhaust.patches_positions.copy()
            exhaust_positions = self.world.fix_view(self.focus_position, view,
                                                    exhaust_positions)
            exhaust_in_view = self.world.positions_in_view(
                self.focus_position, view, exhaust_positions)

            if exhaust_in_view.size:
                exhaust_positions = exhaust_positions[exhaust_in_view]
                exhaust_patches = self.world.fix_view(
                    self.focus_position, view,
                    self.exhaust.patches[exhaust_in_view])

                if self.camera.position[self.Z] < self._culling_height:
                    exhaust_shadows, exhaust_shadow_positions = \
                        e.shadow.get_shadows(exhaust_patches.copy(),
                                             self.world)
                    exhaust_shadows, shadow_depths = \
                        self.camera.get_screen_coordinates(exhaust_shadows)
                    exhaust_shadow_colours = (
                        np.array([[0, 0, 0, 1]]) *
                        np.ones((exhaust_shadows.shape[0], 1)))

                else:
                    exhaust_shadow_positions = np.empty((0, 3))
                    exhaust_shadows = np.empty((0, 4, 2))
                    exhaust_shadow_colours = np.empty((0, 4))

                (exhaust_patches, exhaust_depths) = \
                    self.camera.get_screen_coordinates(exhaust_patches)
                exhaust_colours = self.exhaust.patches_colours[exhaust_in_view]
                exhaust_colours = self.shader.apply_lighting(exhaust_positions,
                                                             exhaust_positions,
                                                             exhaust_colours,
                                                             scatter=False)
            else:
                exhaust_positions = np.empty((0, 3))
                exhaust_patches = np.empty((0, 3, 2))
                exhaust_colours = np.empty((0, 4))

                exhaust_shadow_positions = np.empty((0, 3))
                exhaust_shadows = np.empty((0, 4, 2))
                exhaust_shadow_colours = np.empty((0, 4))

        else:
            exhaust_positions = np.empty((0, 3))
            exhaust_patches = np.empty((0, 3, 2))
            exhaust_colours = np.empty((0, 4))

            exhaust_shadow_positions = np.empty((0, 3))
            exhaust_shadows = np.empty((0, 4, 2))
            exhaust_shadow_colours = np.empty((0, 4))

        # aggregate draw data:
        object_positions = np.r_[player_positions, shots_positions,
                                 exhaust_positions]
        object_patches = list(player_patches[:])
        object_patches.extend(list(shots_patches[:]))
        object_patches.extend(list(exhaust_patches[:]))
        object_colours = np.r_[player_colours, shots_colours, exhaust_colours]

        shadow_positions = np.r_[player_shadow_positions,
                                 shots_shadow_positions,
                                 exhaust_shadow_positions]
        shadow_patches = list(player_shadow[:])
        shadow_patches.extend(list(shots_shadows[:]))
        shadow_patches.extend(list(exhaust_shadows[:]))
        shadow_colours = np.r_[player_shadow_colours, shots_shadow_colours,
                               exhaust_shadow_colours]

        # sort patches:

        # draw:
        surface.fill((0, 0, 0))

        # draw landscape:
        self.draw_patches(map_positions, map_patches, map_colours, surface)

        # draw shadows:
        self.draw_patches(shadow_positions, shadow_patches, shadow_colours,
                          surface)

        # draw objects and particles:
        self.draw_patches(object_positions, object_patches, object_colours,
                          surface)

        if self._pause:

            colour = (204, 153, 153, 153)

            text = self._font.render("press TAB to UNPAUSE", True, colour)

            textpos = text.get_rect(center=(self.config["resolution"][0] / 2,
                                            self.config["resolution"][1] / 2))

            surface.blit(text, textpos)

        else:

            self.player.move()
            self.player.impose_boundary_conditions(self.world)

            if self.shots.number:
                shrapnel = self.shots.move()
                """ create shrapnel """
                self.shots.impose_boundary_conditions(self.world)

            if self.shrapnel.number:
                self.shrapnel.impose_boundary_conditions(self.world)
                self.shrapnel.move()

            if self.exhaust.number:
                self.exhaust.impose_boundary_conditions(self.world)
                self.exhaust.move()

            self.update_camera()

        return flag
