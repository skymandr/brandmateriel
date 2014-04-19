import numpy as np

CONFIG = {
            'resolution':   np.array([640, 480]),
            'dimensions':   np.array([12.0, 9.0]),
            'cameradist':   np.array([6.0, 9.0, 3.0])
         }

RES = CONFIG['resolution'] / CONFIG['dimensions']


def get_screen_coordinates(point, camera, debug=False):
    """
    Calculates screen coordinate of point, based on geometry of camera setup
    relative to the view-screen and the camera position.
    """

    if debug:
        x = (CONFIG['cameradist'][0] + CONFIG['cameradist'][1] *
                (point[0] - camera[0]) / (point[1] - camera[1]))
        y = (CONFIG['dimensions'][1] -
                CONFIG['cameradist'][2] + CONFIG['cameradist'][1] *
                (point[2] - camera[2]) / (point[1] - camera[1]))
    else:
        x = (CONFIG['cameradist'][0] + CONFIG['cameradist'][1] *
                (point[0] - camera[0]) / (point[1] - camera[1]))
        y = (CONFIG['cameradist'][2] - CONFIG['cameradist'][1] *
                (point[2] - camera[2]) / (point[1] - camera[1]))

    return np.array([x * RES[0], y * RES[1]])


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

    scene = np.c_[x.ravel(), y.ravel(), z.ravel()].T

    return scene


def do_demo(filename='demodata.npy', cam=None):
    import matplotlib.pyplot as plt

    scene = get_scene(filename)
    if cam is None:
        cam = np.array([scene[0].mean(), -2 * np.ceil(scene[2].max())- 9.0,
                2 * np.ceil(scene[2].max()) + 6.0])

    pixels = get_screen_coordinates(scene, cam, True)

    f = plt.figure(1)
    f.clf()
    plt.scatter(pixels[0], pixels[1], s=1)
    plt.axis([0, CONFIG['resolution'][0], 0, CONFIG['resolution'][1]])
    plt.grid('on')
    if filename is not None:
        z = np.load(filename)
        plt.imshow(z, extent=[20, 20 + 2 * z.shape[1],
                              CONFIG['resolution'][1] - 20 - 2 * z.shape[0],
                              CONFIG['resolution'][1] - 20],
                   cmap=plt.cm.terrain)

    return scene, cam


