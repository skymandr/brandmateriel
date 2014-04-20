import numpy as np


class Map(object):
    """
    Here be description.
    """

    def __init__(self, filename='demodata.npy'):
        if filename is None:
            z = np.zeros([10, 13])
        else:
            self.raw_map = np.load(filename)

        self.make_patches()
        self.calc_positions()
        self.calc_normals()
        self.colourise()

    def make_patches(self):
        # Get coordinates:
        Y, X = np.mgrid[self.raw_map.shape[0]: 0: -1, 0: self.raw_map.shape[1]]

        # Ininitalise patches:
        self.patches = np.zeros((self.raw_map.shape[1] - 1,
                                 self.raw_map.shape[0] - 1, 4, 3))

        # Fill patches:
        # This for-lops can and should be removed:
        for x in xrange(self.patches.shape[0]):
            for y in xrange(self.patches.shape[1]):
                self.patches[x, y, :, 0] = X[y: y + 2, x: x + 2]
                self.patches[x, y, :, 1] = Y[y: y + 2, x: x + 2]
                self.patches[x, y, :, 2] = self.raw_map[y: y + 2, x: x + 2]

    def colourise(self):
        pass

    def calc_positions(self):
        pass

    def calc_normals(self):
        pass
