

from __future__ import print_function

import numpy as np
import old_camera as c


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


def do_demo(filename='demodata.npy', cam=None, look_at=None):
    import matplotlib.pyplot as plt

    scene = get_scene(filename)

    if cam is None:
        cam = c.Camera(position=np.array([scene[:, 0].mean(),
                       -2 * np.ceil(scene[:, 2].max()) - 9.0,
                       2 * np.ceil(scene[:, 2].max()) + 6.0]),
                       resolution=np.array([640, 480]),
                       mpldebug=True)

    if look_at is not None:
        cam.look_at_point(look_at)

    pixels = cam.get_screen_coordinates(scene)

    f = plt.figure(1)
    f.clf()
    plt.scatter(pixels[:, 0], pixels[:, 1], s=1)
    plt.axis([0, cam.screen.resolution[0], 0, cam.screen.resolution[1]])
    plt.grid('on')

    if filename is not None:
        z = np.load(filename)
        plt.imshow(z, extent=[20, 20 + 2 * z.shape[1],
                              cam.screen.resolution[1] - 20 - 2 * z.shape[0],
                              cam.screen.resolution[1] - 20],
                   cmap=plt.cm.terrain)

    return scene, cam


def do_live_demo(steps=42, delay=0.125, save_fig=False):
    import string
    import time
    import matplotlib.pyplot as plt

    look_at = np.array([31, 33, 21])
    s, c = do_demo()

    angles = np.linspace(0, 2 * np.pi, steps + 1)
    R = np.linalg.norm(c.position[: 2] - look_at[: 2])

    for n, a in enumerate(angles):
        t0 = time.time()
        c.position = np.array([np.sin(a) * R + 31, np.cos(a) * R + 33, 42])
        s, c = do_demo(cam=c, look_at=look_at)
        plt.axis('off')
        plt.draw()
        if save_fig:
            plt.savefig('out/{0}.png'.format(string.zfill(str(n), 2)))

        while(time.time() - t0 < delay):
            pass
