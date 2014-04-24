import numpy as np


class FireFighter(object):
    """
    Patches for FireFighter.
    """

    X = U = 0
    Y = V = 1
    Z = W = 2

    def __init__(self, basecolour=np.array([0, 204, 0, 255])):
        points = np.array([[0.5, 1.0, 0.0],     # 0
                           [-0.5, 1.0, 0.0],    # 1
                           [-1.0, 0.0, 0.2],    # 2
                           [0.0, -1.0, 0.0],    # 3
                           [1.0, 0.0, 0.2],     # 4
                           [0.0, -0.5, 0.5],    # 5
                           [0.10, 0.1, 0.0],    # 6
                           [-.10, 0.1, 0.0],    # 7
                           [0.0, -0.2, 0.0],    # 8
                           ])

        self._patches = np.array([
            [points[0], points[1], points[5]],  # 0: front
            [points[1], points[2], points[5]],  # 1: front left
            [points[2], points[3], points[5]],  # 2: back left
            [points[3], points[4], points[5]],  # 3: back right
            [points[4], points[0], points[5]],  # 4: front right
            [(points[1] + points[0]) * 0.5,     # 5: bottom front centre
             points[6], points[7]],
            [(points[1] + points[0]) * 0.5,     # 6: bottom front left
             points[7], points[1]],
            [(points[1] + points[0]) * 0.5,     # 7: bottom front right
             points[0], points[6]],
            [points[1], points[7], points[3]],  # 8: bottom left front
            [points[7], points[8], points[3]],  # 9: bottom left back
            [points[6], points[0], points[3]],  # A: bottom right front
            [points[8], points[6], points[3]],  # B: bottom right back
            [points[3], points[2], points[1]],  # C: bottom left wing
            [points[3], points[0], points[4]],  # D: bottom right wing
            [points[8], points[7], points[6]],  # E: engine A
            ])

        self._colours = np.array([[0, 204, 0, 255],
                                  [0, 153, 0, 255],
                                  [0, 204, 0, 255],
                                  [0, 204, 0, 255],
                                  [0, 153, 0, 255],
                                  [0, 0, 153, 255],
                                  [0, 0, 153, 255],
                                  [0, 0, 153, 255],
                                  [0, 0, 153, 255],
                                  [0, 0, 153, 255],
                                  [0, 0, 153, 255],
                                  [0, 0, 153, 255],
                                  [0, 0, 240, 255],
                                  [0, 0, 240, 255],
                                  [240, 240, 0, 255],
                                  ])

        self._orientation = np.array([[1.0, 0.0, 0.0],  # U
                                      [0.0, 1.0, 0.0],  # V
                                      [0.0, 0.0, 1.0]   # W
                                      ])

        self._basecolour = basecolour

        self._position = np.array([0.0, 0.0, 0.0])

        self._calc_normals()

        self._calc_positions()
        print self.patches.shape, self.positions.shape

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

        self._positions = self._patches.mean(1)

    def _calc_normals(self):
        normals = np.zeros([self._patches.shape[0], 3])

        v0s = self._patches[:, 1] - self._patches[:, 0]
        v1s = self._patches[:, 2] - self._patches[:, 1]

        normals = np.cross(v0s, v1s)
        normals /= np.sqrt((normals ** 2).sum(-1))[:, np.newaxis]

        self._normals = normals
