import numpy as np


class FireFighter(object):
    """
    Patches for FireFighter.
    """

    X = U = 0
    Y = V = 1
    Z = W = 2

    def __init__(self, basecolour=np.array([0, 204, 0])):
        points = np.array([[0.5, 1.0, 0],
                        [-0.5, 1.0, 0],
                        [-1.0, 0.0, 0.2],
                        [0.0, -1.0, 0.0],
                        [1.0, 0.0, 0.2],
                        [0.0, -0.5, 0.5]])

        self._patches = np.array([
            [points[0], points[1], points[5]],  # front
            [points[1], points[2], points[5]],  # front left
            [points[2], points[3], points[5]],  # back left
            [points[3], points[4], points[5]],  # back right
            [points[4], points[0], points[5]],  # front right
            [points[3], points[1], points[1]],  # bottom
            [points[3], points[2], points[1]],  # bottom left
            [points[3], points[0], points[4]]   # bottom right
            ])

        self._colours = np.array([[0, 204, 0],
                                  [0, 153, 0],
                                  [0, 204, 0],
                                  [0, 204, 0],
                                  [0, 153, 0],
                                  [0, 0, 153],
                                  [0, 0, 240],
                                  [0, 0, 240]
                                  ])

        self._orientation = np.array([[1.0, 0.0, 0.0],  # U
                                      [0.0, 1.0, 0.0],  # V
                                      [0.0, 0.0, 1.0]   # W
                                      ])

        self._basecolour = basecolour

        self._position = np.array([0.0, 0.0, 0.0])

        self._calc_normals()

        self._calc_positions()

        self._colourise()

    @property
    def position(self):
        return self._position

    @position.setter
    def position(self, val):
        self._position = val

    @property
    def patches(self):
        return self._patches + self.position[np.newaxis, np.newaxis, :]

    @property
    def normals(self):
        return self._normals

    @property
    def positions(self):
        return self._positions + self.position[np.newaxis, :]

    @property
    def colours(self):
        return self._colours

    @property
    def basecolour(self):
        return self._basecolour

    @basecolour.setter
    def basecolour(self, val):
        self._basecolour = val

    def _colourise(self):
        """
        Not yet fully implemented, but should assign colours (with some sort of
        noise) to patches.

        Currently debug wit just green and blue.
        """
        # colours = np.zeros([self._patches.shape[0], 3], dtype=np.int)

        # self._colours = colours + self.basecolour

    def _calc_positions(self):
        """
        Useful for sorting and the like, maybe.
        """

        self._positions = self._patches.mean(2)

    def _calc_normals(self):
        normals = np.zeros([self._patches.shape[0], 3])

        v0s = self._patches[:, 1] - self._patches[:, 0]
        v1s = self._patches[:, 2] - self._patches[:, 1]

        normals = np.cross(v0s, v1s)
        normals /= np.sqrt((normals ** 2).sum(-1))[:, np.newaxis]

        self._normals = normals
