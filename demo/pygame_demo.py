#! /usr/bin/env python

import sys
import numpy as np
import pygame
import pygame.locals as l
import camera as c
import mapper as m
import shader as s
import triDobjects as o
import contextlib
import cStringIO

RESOLUTION = np.array([640, 480])
KEYBOARD = {l.K_UP: 'up', l.K_k: 'up',
            l.K_DOWN: 'down', l.K_j: 'down',
            l.K_LEFT: 'left', l.K_h: 'left',
            l.K_RIGHT: 'right', l.K_l: 'right',
            l.K_a: 'a', l.K_s: 'b', l.K_d: 'c',
            l.K_RETURN: 'start', l.K_SPACE: 'start',
            l.K_ESCAPE: 'quit', l.K_F1: 'help'}

if not pygame.font:
    print "Warning: no fonts detected; fonts disabled."

if not pygame.mixer:
    print "Warning: no sound detected; sound disabled."


@contextlib.contextmanager
def silence():
    """
    Ye olde silencer
    """
    save_stdout = sys.stdout
    sys.stdout = cStringIO.StringIO()
    yield
    sys.stdout = save_stdout


def handle_inputs():
    """ Should later handle inputs from user. """
    flag = True
    for event in pygame.event.get():
        if event.type == l.QUIT:
            flag = close() and flag
        elif event.type == l.KEYDOWN:
            flag = relay_input(event.key) and flag
        else:
            print "Unknown event: \n{0}\n({1})".format(event, event.type)

    return flag


def relay_input(event_key):
    if event_key in KEYBOARD.keys():
        print "Key pressed: {0} ({1})".format(KEYBOARD[event_key],
                                              str(event_key))
        if KEYBOARD[event_key] == 'quit':
            return close()
    else:
        print "Unknown key pressed. ({0})".format(str(event_key))

    return True


def close():
    """ Close game. """
    print "Quitting game..."
    pygame.quit()
    return False


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

    # pixels = cam.get_screen_coordinates(scene.positions)
    colours = shader.apply_lighting(scene.positions, scene.normals,
                                    scene.colours.copy())
    patches, depth = cam.get_screen_coordinates(scene.patches)

    order = np.argsort(-((scene.positions - cam.position) ** 2).mean(-1))

    for n in order:
        # Use this to render point cloud in uniform colour:
        # screen.set_at(np.round(pixels[n]).astype(np.int), (204, 0, 0))

        # Use this to render point cloud in shaded colours (not pretty):
        # screen.set_at(np.round(pixels[n]).astype(np.int), colours[n, :])

        # Use this to render patches:
        pygame.draw.polygon(screen, colours[n], patches[n])

    pygame.display.flip()

    return scene, cam


def do_live_demo(filename='demodata.npy', sealevel=7.0, steps=42, fps=30,
                 save_fig=False):
    import string
    fps_clock = pygame.time.Clock()
    screen = pygame.display.set_mode(RESOLUTION, pygame.DOUBLEBUF)

    scene = m.Map(filename, sealevel, True)
    look_at = np.array([31, 33, 21])
    cam = c.Camera(position=np.array([scene.positions[:, 0].mean(),
                   -2 * np.ceil(scene.positions[:, 2].max()) - 9.0,
                   2 * np.ceil(scene.positions[:, 2].max()) + 6.0]),
                   screen=c.Screen(resolution=np.array(RESOLUTION)))

    shader = s.Shader(cam)

    angles = np.linspace(0, 2 * np.pi, steps + 1)
    R = np.linalg.norm(cam.position[: 2] - look_at[: 2])

    for N, a in enumerate(angles):
        screen.fill((0, 0, 0))
        cam.position = np.array([np.sin(a) * R + 31, np.cos(a) * R + 33, 42])
        cam.look_at_point(look_at)

        # pixels = cam.get_screen_coordinates(scene.positions)
        colours = shader.apply_lighting(scene.positions, scene.normals,
                                        scene.colours.copy())
        patches, depth = cam.get_screen_coordinates(scene.patches)

        order = np.argsort(-((scene.positions - cam.position) ** 2).mean(-1))

        for n in order:
            # Use this to render point cloud in uniform colour:
            # screen.set_at(np.round(pixels[n]).astype(np.int), (204, 0, 0))

            # Use this to render point cloud in shaded colours (not pretty):
            # screen.set_at(np.round(pixels[n]).astype(np.int), colours[n, :])

            # Use this to render patches:
            pygame.draw.polygon(screen, colours[n], patches[n])

        pygame.display.flip()

        if save_fig:
            pygame.image.save(screen,
                              'out/{0}.png'.format(string.zfill(str(N), 2)))

        fps_clock.tick(fps)


def do_brand_demo(filename='zdata.npy', sealevel=0.0, steps=42, fps=30,
                  save_fig=False, frames=None):
    import string
    fps_clock = pygame.time.Clock()
    screen = pygame.display.set_mode(RESOLUTION, pygame.DOUBLEBUF)

    scene = m.Map(filename, sealevel, True)
    look_at = np.array([63.5, 63.5, 6.0])
    cam = c.Camera(position=np.array([54.5, 63.5, 6.0]),
                   screen=c.Screen(resolution=np.array(RESOLUTION)))

    shader = s.Shader(cam)

    fighter = o.FireFighter()

    fighter.position = np.array([63.5, 63.5, 6.0])

    house = o.House()

    house.position = np.array([58.5, 67, 2.23])

    house.yaw = np.pi / 8

    angles = np.linspace(0, 2 * np.pi, steps + 1)
    R = np.linalg.norm(cam.position[: 2] - look_at[: 2])

    for N, a in enumerate(angles):
        screen.fill((0, 0, 0))
        cam.position = np.array([np.sin(a) * R + 63.5,
                                 np.cos(a) * R + 63.5, 6.0])
        cam.look_at_point(look_at)

        colours = shader.apply_lighting(scene.positions, scene.normals,
                                        scene.colours.copy())

        patches, depth = cam.get_screen_coordinates(scene.patches)

        order = np.argsort(-((scene.positions - cam.position) ** 2).mean(-1))

        for n in order:
            if ((depth[n].mean() > 0 and patches[n] >= 0).any() and
                    (patches[n, :, 0] < RESOLUTION[0]).any() and
                    (patches[n, :, 1] < RESOLUTION[1]).any()):

                pygame.draw.polygon(screen, colours[n], patches[n])

        fighter.yaw = a

        fighter.pitch = a

        fighter.roll = a

        colours = shader.apply_lighting(fighter.positions, fighter.normals,
                                        fighter.colours.copy())

        patches, depth = cam.get_screen_coordinates(fighter.patches)

        order = np.argsort(-((fighter.positions - cam.position) ** 2).mean(-1))

        for n in order:
            if (colours[n, 3] and depth[n].mean() > 0 and
                    (patches[n] >= 0).any() and
                    (patches[n, :, 0] < RESOLUTION[0]).any() and
                    (patches[n, :, 1] < RESOLUTION[1]).any()):
                pygame.draw.polygon(screen, colours[n], patches[n])

        colours = shader.apply_lighting(house.positions, house.normals,
                                        house.colours.copy())

        patches, depth = cam.get_screen_coordinates(house.patches)

        order = np.argsort(-((house.positions - cam.position) ** 2).mean(-1))

        for n in order:
            if (colours[n, 3] and depth[n].mean() > 0 and
                    (patches[n] >= 0).any() and
                    (patches[n, :, 0] < RESOLUTION[0]).any() and
                    (patches[n, :, 1] < RESOLUTION[1]).any()):
                pygame.draw.polygon(screen, colours[n], patches[n])

        pygame.display.flip()

        if save_fig:
            pygame.image.save(screen,
                              'out/{0}.png'.format(string.zfill(str(N), 2)))

        the_tick = fps_clock.tick(fps)
        print "Frame upate time: {0} ms".format(the_tick)

        if not frames is None:
            frames.append(the_tick/1000.0)


def print_cpu_model():
    """
    get cpu model, in a very hacky way
    """

    from subprocess import check_output

    command = "cat /proc/cpuinfo"
    cpuinfo = check_output(command, shell=True).strip()

    for ln in cpuinfo.split("\n"):
        if "model name" in ln:
            print "Cpu Model:", ln.split(":")[1]
            return

def benchmark_demo():
    """
    run do_brand_demo and benchmark fps
    """
    print "Running Benchmarks, silent, virtualdisplay"
    print "Don't Panic! This will take a moment.\n\n"

    from pyvirtualdisplay import Display
    display = Display(visible=0, size=(1440, 900))
    display.start()

    pygame.init()
    fps = []
    with silence():
        do_brand_demo(save_fig=False, frames=fps)

    print "Benchmarking On"
    print_cpu_model()

    print "fps stats"
    print "Mean: %0.4f\nMedian: %0.4f\nVariance: %0.4f" % \
        (np.average(fps), np.median(fps), np.var(fps))
    print "Min: %0.4f\nMax: %0.4f" % \
        (min(fps), max(fps))
    print "Total Frames:", len(fps)

    return 0


def main():
    pygame.init()
    frames = []
    do_brand_demo(save_fig=False)

    pygame.mouse.set_visible(False)
    while(handle_inputs()):
        pygame.event.set_grab(False)
        if pygame.mouse.get_focused():
            pygame.event.set_grab(True)
            pygame.mouse.set_pos(RESOLUTION / 2)


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description='Shady Pretty Doings.')
    parser.add_argument(
        '-b', '--benchmark',
        help="Run benchmark", action="store_true")
    args = parser.parse_args()

    if args.benchmark:
        sys.exit(benchmark_demo())
    else:
        sys.exit(main())
