# TODO:
# * Vegetation:
#   - spruce
#   - tall tree
#   - lower tree
#   - birch (kill!)
#   - shrub
#
# * Buildings:
#   - Simple house (DONE)
#   - Nicer roofed house (very simple)
#   - Cottage (quite simple)
#   - Tent (quite simple)
#   - Radar (animated?)
#
# * Stuff:
#   - Rocket
#   - Firestarter
#   - Hunter-seeker
#   - Noch Less
#   - Fire
#   - Particles

import numpy as np


class TriD(object):
    """
    Parent class for TriD-objects.
    """

    X = U = 0
    Y = V = 1
    Z = W = 2

    def __init__(self, basecolour=np.array([0, 204, 0, 255]),
                 position=np.array([0.0, 0.0, 0.0]),
                 yaw=0.0, pitch=0.0, roll=0.0):
        points = np.array([[1.0, 0.0, -1.0 / np.sqrt(2)],   # 0
                           [-1.0, 0.0, -1.0 / np.sqrt(2)],  # 1
                           [0.0, -1.0, 1.0 / np.sqrt(2)],   # 2
                           [0.0, 1.0, 1.0 / np.sqrt(2)],    # 3
                           ])

        self._patches = np.array([
            [points[1], points[2], points[3]],  # left side
            [points[1], points[0], points[2]],  # back side
            [points[0], points[3], points[2]],  # right side
            [points[0], points[1], points[3]],  # front side
            ])

        self._colours = np.array([[204, 0, 255],
                                  [0, 204, 0, 255],
                                  [0, 0, 204, 255],
                                  [204, 204, 204, 255],
                                  ])

        self._orientation = np.array([[1.0, 0.0, 0.0],  # U
                                      [0.0, 1.0, 0.0],  # V
                                      [0.0, 0.0, 1.0]   # W
                                      ])

        self._basecolour = basecolour

        self._position = position

        self._yaw = yaw

        self._pitch = pitch

        self._roll = roll

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

    @property
    def yaw(self):
        return self._yaw

    @yaw.setter
    def yaw(self, val):
        self._yaw = val

    @property
    def pitch(self):
        return self._pitch

    @pitch.setter
    def pitch(self, val):
        self._pitch = val

    @property
    def roll(self):
        return self._roll

    @roll.setter
    def roll(self, val):
        self._roll = val

    @property
    def bounding_box(self):
        return np.c_[self.positions.min(0), self.positions.max(0)].T

    def _colourise(self):
        """
        Not yet fully implemented, but should assign colours...
        """
        # colours = np.zeros([self._patches.shape[0], 3], dtype=np.int)

        # self._colours = colours + self.basecolour

        pass

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


class FireFighter(TriD):
    """
    Patches for FireFighter.
    """

    def __init__(self, basecolour=np.array([0, 204, 0, 255]),
                 position=np.array([0.0, 0.0, 0.0]),
                 yaw=0.0, pitch=0.0, roll=0.0):
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
                                  [0, 0, 204, 255],
                                  [0, 0, 204, 255],
                                  [204, 204, 0, 255],
                                  ])

        self._orientation = np.array([[1.0, 0.0, 0.0],  # U
                                      [0.0, 1.0, 0.0],  # V
                                      [0.0, 0.0, 1.0]   # W
                                      ])

        self._basecolour = basecolour

        self._position = position

        self._yaw = yaw

        self._pitch = pitch

        self._roll = roll

        self._calc_normals()

        self._calc_positions()

        self._colourise()


class House(TriD):
    """
    Patches for House.
    """

    def __init__(self, basecolour=np.array([0, 204, 0, 255]),
                 position=np.array([0.0, 0.0, 0.0]),
                 yaw=0.0, pitch=0.0, roll=0.0):
        points = np.array([[0.7, 1.25, 0.0],       # 0
                           [-0.7, 1.25, 0.0],      # 1
                           [-0.7, -1.25, 0.0],     # 2
                           [0.7, -1.25, 0.0],      # 3
                           [0.7, 1.25, 0.7],      # 4
                           [-0.7, 1.25, 0.7],     # 5
                           [-0.7, -1.25, 0.7],    # 6
                           [0.7, -1.25, 0.7],     # 7
                           [0.0, 1.25, 1.0],       # 8
                           [0.0, -1.25, 1.0],      # 9
                           ])

        self._patches = np.array([
            [points[0], points[1], points[4]],  # N bottom
            [points[4], points[1], points[5]],  # N mid
            [points[4], points[5], points[8]],  # N top
            [points[2], points[3], points[6]],  # S bottom
            [points[6], points[3], points[7]],  # S mid
            [points[6], points[7], points[9]],  # S top
            [points[1], points[2], points[5]],  # W bottom
            [points[5], points[2], points[6]],  # W top
            [points[3], points[0], points[7]],  # E bottom
            [points[7], points[0], points[4]],  # E top
            [points[5], points[6], points[9]],  # W roof bottom
            [points[9], points[8], points[5]],  # W roof top
            [points[7], points[4], points[9]],  # E roof bottom
            [points[9], points[4], points[8]],  # E roof top
            ])

        self._colours = np.array([[153, 153, 102, 255],
                                  [153, 153, 102, 255],
                                  [153, 153, 102, 255],
                                  [153, 153, 102, 255],
                                  [153, 153, 102, 255],
                                  [153, 153, 102, 255],
                                  [102, 102, 102, 255],
                                  [102, 102, 102, 255],
                                  [102, 102, 102, 255],
                                  [102, 102, 102, 255],
                                  [0, 102, 0, 255],
                                  [0, 102, 0, 255],
                                  [0, 102, 0, 255],
                                  [0, 102, 0, 255],
                                  ])

        self._orientation = np.array([[1.0, 0.0, 0.0],  # U
                                      [0.0, 1.0, 0.0],  # V
                                      [0.0, 0.0, 1.0]   # W
                                      ])

        self._basecolour = basecolour

        self._position = position

        self._yaw = yaw

        self._pitch = pitch

        self._roll = roll

        self._calc_normals()

        self._calc_positions()

        self._colourise()
