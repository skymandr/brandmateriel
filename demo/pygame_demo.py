#! /usr/env python

import sys
import numpy as np
import pygame
# import pygame.locals as pgl
import camera as c
import mapper as m
import shader as s

RESOLUTION = (640, 480)

if not pygame.font:
    print "Warning: no fonts detected; fonts disabled."

if not pygame.mixer:
    print "Warning: no sound detected; sound disabled."


def get_scene(filename=None):
    """
    Initialise scene.

    By default just flat test surface, but can also load Numpy compatible
    2D-height data.
    """

    if filename is None:
        x, y, z = np.mgrid[0: 13, 0: 10, 0: 1]
    else:
        z = np.load(filename)
        y, x = np.mgrid[z.shape[0]: 0: -1, 0: z.shape[1]]

    scene = np.c_[x.ravel(), y.ravel(), z.ravel()]

    return scene


def do_demo(filename='demodata.npy', cam=None, look_at=None, sealevel=0):
    screen = pygame.display.set_mode(RESOLUTION, pygame.DOUBLEBUF)
    scene = m.Map(filename, sealevel)

    if cam is None:
        cam = c.Camera(position=np.array([scene.positions[:, 0].mean(),
                       -2 * np.ceil(scene.positions[:, 2].max()) - 9.0,
                       2 * np.ceil(scene.positions[:, 2].max()) + 6.0]),
                       screen=c.Screen(resolution=np.array(RESOLUTION)))

    shader = s.Shader(cam)

    if look_at is not None:
        cam.look_at_point(look_at)

    pixels = cam.get_screen_coordinates(scene.positions)
    colours = shader.apply_lighting(scene.positions, scene.normals,
                                    scene.colours.copy())
    patches = cam.get_screen_coordinates(scene.patches)

    # Use PixelArray instead:
    for n, p in enumerate(pixels):
        # Use this to render point cloud in uniform colour:
        # screen.set_at(np.round(p).astype(np.int), (204, 0, 0))

        # Use this to render point cloud in shaded colours (not pretty):
        # screen.set_at(np.round(p).astype(np.int), colours[n, :])

        # Use this to (maybe) render patches:
        pygame.draw.polygon(screen, colours[n], patches[n * 4: n * 4 + 4])

    pygame.display.flip()

    return scene, cam


def do_live_demo(filename='demodata.npy', sealevel=7.0, steps=42, fps=30,
                 save_fig=False):
    import string
    fps_clock = pygame.time.Clock()
    screen = pygame.display.set_mode(RESOLUTION, pygame.DOUBLEBUF)

    scene = m.Map(filename, sealevel, False)
    look_at = np.array([31, 33, 21])
    cam = c.Camera(position=np.array([scene.positions[:, 0].mean(),
                   -2 * np.ceil(scene.positions[:, 2].max()) - 9.0,
                   2 * np.ceil(scene.positions[:, 2].max()) + 6.0]),
                   screen=c.Screen(resolution=np.array(RESOLUTION)))

    shader = s.Shader(cam)

    angles = np.linspace(0, 2 * np.pi, steps + 1)
    R = np.linalg.norm(cam.position[: 2] - look_at[: 2])

    for n, a in enumerate(angles):
        screen.fill((0, 0, 0))
        cam.position = np.array([np.sin(a) * R + 31, np.cos(a) * R + 33, 42])
        cam.look_at_point(look_at)
        pixels = cam.get_screen_coordinates(scene.positions)
        colours = shader.apply_lighting(scene.positions, scene.normals,
                                        scene.colours.copy())
        patches = cam.get_screen_coordinates(scene.patches)

        # Use PixelArray instead:
        for n, p in enumerate(pixels):
            # Use this to render point cloud in uniform colour:
            # screen.set_at(np.round(p).astype(np.int), (204, 0, 0))

            # Use this to render point cloud in shaded colours (not pretty):
            # screen.set_at(np.round(p).astype(np.int), colours[n, :])

            # Use this to (maybe) render patches:
            pygame.draw.polygon(screen, colours[n], patches[n * 4: n * 4 + 4])

        pygame.display.flip()

        if save_fig:
            pygame.image.save(screen,
                              'out/{0}.png'.format(string.zfill(str(n), 2)))

        fps_clock.tick(fps)


def main():
    pygame.init()
    # do_demo()
    do_live_demo(save_fig=False)


if __name__ == "__main__":
    sys.exit(main())
