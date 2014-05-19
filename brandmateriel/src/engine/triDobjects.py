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
                 yaw=0.0, pitch=0.0, roll=0.0, scale=1.0):
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

        self._scale = scale

        self._engine = np.array([0.0, 0.0, 0.0])

        self._gun = np.array([0.0, 0.0, 0.0])

    @property
    def orientation(self):
        return self._apply_rotation(self._orientation)

    @property
    def centre_of_mass(self):
        return self.patches.mean(0).mean(0)

    @property
    def position(self):
        return self._position

    @position.setter
    def position(self, val):
        self._position = val

    @property
    def patches(self):
        return (self._scale * self._apply_rotation(self._patches) +
                self.position[np.newaxis, np.newaxis, :])

    @property
    def normals(self):
        return self._apply_rotation(self._normals)

    @property
    def positions(self):
        return (self._scale * self._apply_rotation(self._positions) +
                self.position[np.newaxis, :])

    @property
    def engine(self):
        return (self._scale * self._apply_rotation(self._engine) +
                self.position)

    @property
    def gun(self):
        return (self._scale * self._apply_rotation(self._gun) + self.position)

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
    def scale(self):
        return self._scale

    @scale.setter
    def scale(self, val):
        self._scale = val

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

    def _apply_rotation(self, positions):
        y = self.yaw
        p = self.pitch
        r = self.roll

        Rx = np.array([[1, 0, 0],
                       [0, np.cos(p), - np.sin(p)],
                       [0, np.sin(p), np.cos(p)]])

        Ry = np.array([[np.cos(r), 0, np.sin(r)],
                       [0, 1, 0],
                       [-np.sin(r), 0, np.cos(r)]])

        Rz = np.array([[np.cos(y), np.sin(y), 0],
                       [-np.sin(y), np.cos(y), 0],
                       [0, 0, 1]])

        return np.inner(positions, np.dot(Ry, np.dot(Rx, Rz)).T)


class FireFighter(TriD):
    """
    Patches for FireFighter.
    """
    def __init__(self, basecolour=np.array([204, 0, 0, 255]),
                 position=np.array([0.0, 0.0, 0.0]),
                 yaw=0, pitch=0, roll=0, scale=1.0):
        points = np.array([
            # Bottom:
            [0, 0.5, 0],         # 0
            [-0.5, -.25, 0],     # 1
            [0.5, -.25, 0],      # 2
            # Middle:
            [0.15, 0.7, 0.17],   # 3
            [-0.15, 0.7, 0.17],  # 4
            [-0.7, 0.0, 0.1],    # 5
            [0.0, -0.5, 0.1],    # 6
            [0.7, 0.0, 0.1],     # 7
            # Top:
            [0.0, 0.2, 0.3],     # 8
            [0.0, 0.0, 0.2],     # 9
            ])

        es = 0.17
        offset = np.array([0.0, 0.0, 0.0])
        points += offset

        self._patches = np.array([
            # Bottom:
            [points[1], points[0], points[0] * es],                       # FP
            [points[1], points[0] * es, points[1] * es],                  # MP
            [points[1], points[1] * es, points[(1, 2), :].mean(0)],       # BP
            [points[2], points[0] * es, points[0]],                       # FS
            [points[2], points[2] * es, points[0] * es],                  # MS
            [points[2], points[(1, 2), :].mean(0), points[2] * es],       # BS
            [points[(1, 2), :].mean(0), points[1] * es, points[2] * es],  # B
            # Engine:
            [points[0] * es, points[2] * es, points[1] * es],
            # Bow:
            [points[0], points[4], points[3]],                  # Front
            [points[0], points[(0, 1), :].mean(0), points[4]],  # F Port
            [points[0], points[3], points[(0, 2), :].mean(0)],  # F Starboard
            # Bottom Stern:
            [points[6], points[1], points[2]],
            # Bottom Port:
            [points[1], points[5], points[(0, 1), :].mean(0)],
            # Bottom Starboard:
            [points[7], points[2], points[(0, 2), :].mean(0)],
            # Cockpit:
            [points[3], points[4], points[8]],                  # Glass
            [points[4], points[(0, 1), :].mean(0), points[8]],  # F Port
            [points[8], points[(0, 2), :].mean(0), points[3]],  # F Starboard
            [points[8], points[(0, 1), :].mean(0), points[9]],  # B Port
            [points[9], points[(0, 2), :].mean(0), points[8]],  # B Starboard
            # Stern:
            [points[1], points[6], points[9]],  # Port
            [points[6], points[2], points[9]],  # Starboard
            # Wings:
            [points[5], points[9], points[(0, 1), :].mean(0)],  # P Front
            [points[5], points[1], points[9]],                  # P Back
            [points[7], points[(0, 2), :].mean(0), points[9]],  # S Front
            [points[7], points[9], points[2]],                  # S Back
            ])

        points[:, 1] *= np.sqrt(3) / 2.0

        self._colours = np.array([[51, 51, 102, 255],   # Bottom:
                                  [51, 51, 102, 255],
                                  [51, 51, 102, 255],
                                  [51, 51, 102, 255],
                                  [51, 51, 102, 255],
                                  [51, 51, 102, 255],
                                  [51, 51, 102, 255],
                                  [204, 102, 0, 255],   # Engine
                                  [0, 0, 51, 255],    # Bow:
                                  [0, 0, 102, 255],
                                  [0, 0, 102, 255],
                                  [0, 0, 102, 255],     # Stern
                                  [51, 0, 51, 255],     # Bottom Port
                                  [0, 51, 51, 255],     # Bottom Starboard
                                  [51, 153, 153, 255],  # Cockpit:
                                  [153, 0, 0, 255],
                                  [153, 0, 0, 255],
                                  [153, 0, 0, 255],
                                  [153, 0, 0, 255],
                                  [153, 0, 0, 255],  # Stern:
                                  [153, 0, 0, 255],
                                  [153, 0, 0, 255],  # Wings:
                                  [153, 0, 0, 255],
                                  [153, 0, 0, 255],
                                  [153, 0, 0, 255],
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

        self._scale = scale

        self._engine = np.array([0.0, 0.0, 0.0])

        self._gun = self._patches[8].mean(0)


class FireFighterStripes(TriD):
    """
    Patches for FireFighter.
    """
    def __init__(self, basecolour=np.array([204, 0, 0, 255]),
                 position=np.array([0.0, 0.0, 0.0]),
                 yaw=0, pitch=0, roll=0, scale=1.0):
        points = np.array([
            # Bottom:
            [0, 0.5, 0],         # 0
            [-0.5, -.25, 0],     # 1
            [0.5, -.25, 0],      # 2
            # Middle:
            [0.17, 0.7, 0.17],   # 3
            [-0.17, 0.7, 0.17],  # 4
            [-0.7, 0.0, 0.1],    # 5
            [0.0, -0.5, 0.1],    # 6
            [0.7, 0.0, 0.1],     # 7
            # Top
            [0.0, 0.2, 0.3],     # 8
            [0.0, 0.0, 0.2],     # 9
            # Wing details:
            [-0.5875, 0.03125, 0.075],  # 10
            [-0.65, -0.0625, 0.075],    # 11
            [0.65, -0.0625, 0.075],     # 12
            [0.5875, 0.03125, 0.075],   # 13
            ])

        es = 0.17

        self._patches = np.array([
            # Bottom:
            [points[1], points[0], points[0] * es],                       # FP
            [points[1], points[0] * es, points[1] * es],                  # MP
            [points[1], points[1] * es, points[(1, 2), :].mean(0)],       # BP
            [points[2], points[0] * es, points[0]],                       # FS
            [points[2], points[2] * es, points[0] * es],                  # MS
            [points[2], points[(1, 2), :].mean(0), points[2] * es],       # BS
            [points[(1, 2), :].mean(0), points[1] * es, points[2] * es],  # B
            # Engine:
            [points[0] * es, points[2] * es, points[1] * es],
            # Bow:
            [points[0], points[4], points[3]],                  # Front
            [points[0], points[(0, 1), :].mean(0), points[4]],  # F Port
            [points[0], points[3], points[(0, 2), :].mean(0)],  # F Starboard
            # Bottom Stern:
            [points[6], points[1], points[2]],
            # Bottom Port:
            [points[1], points[5], points[(0, 1), :].mean(0)],
            # Bottom Starboard:
            [points[7], points[2], points[(0, 2), :].mean(0)],
            # Cockpit:
            [points[3], points[4], points[8]],                  # Glass
            [points[4], points[(0, 1), :].mean(0), points[8]],  # F Port
            [points[8], points[(0, 2), :].mean(0), points[3]],  # F Starboard
            [points[8], points[(0, 1), :].mean(0), points[9]],  # B Port
            [points[9], points[(0, 2), :].mean(0), points[8]],  # B Starboard
            # Stern:
            [points[1], points[6], points[9]],  # Port
            [points[6], points[2], points[9]],  # Starboard
            # Wings:
            [points[10], points[9], points[(0, 1), :].mean(0)],  # P Front
            [points[11], points[1], points[9]],                  # P Back
            [points[13], points[(0, 2), :].mean(0), points[9]],  # S Front
            [points[12], points[9], points[2]],                  # S Back
            [points[11], points[10], points[5]],                 # P Light
            [points[13], points[12], points[7]],                 # S Light
            [points[11], points[9], points[10]],                 # P Stripe
            [points[13], points[9], points[12]],                 # S Stripe
            ])

        points[:, 1] *= np.sqrt(3) / 2.0

        self._colours = np.array([[51, 51, 102, 255],   # Bottom:
                                  [51, 51, 102, 255],
                                  [51, 51, 102, 255],
                                  [51, 51, 102, 255],
                                  [51, 51, 102, 255],
                                  [51, 51, 102, 255],
                                  [51, 51, 102, 255],
                                  [204, 102, 0, 255],   # Engine
                                  [0, 0, 102, 255],     # Stern:
                                  [0, 0, 102, 255],
                                  [0, 0, 102, 255],
                                  [0, 0, 102, 255],     # Bow
                                  [51, 0, 102, 255],    # Bottom Port
                                  [0, 51, 102, 255],    # Bottom Starboard
                                  [51, 153, 153, 255],  # Cockpit:
                                  [102, 0, 0, 255],
                                  [102, 0, 0, 255],
                                  [102, 0, 0, 255],
                                  [102, 0, 0, 255],
                                  [102, 0, 0, 255],  # Stern:
                                  [102, 0, 0, 255],
                                  [102, 0, 0, 255],  # Wings:
                                  [102, 0, 0, 255],
                                  [102, 0, 0, 255],
                                  [102, 0, 0, 255],
                                  [204, 0, 0, 255],
                                  [0, 204, 0, 255],
                                  [204, 204, 0, 255],
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

        self._scale = scale

        self._engine = np.array([0.0, 0.0, 0.0])

        self._gun = self.patches[8].mean(0)


class Pika(TriD):
    """
    Patches for Pika.
    """
    def __init__(self, basecolour=np.array([204, 204, 204, 255]),
                 position=np.array([0.0, 0.0, 0.0]),
                 yaw=0, pitch=0, roll=0, scale=1.0):
        points = np.array([[0.0, 0.35, 0.05],   # 0
                           [-0.1, 0.1, 0.05],   # 1
                           [-0.2, 0.1, 0.05],   # 2
                           [-0.6, 0.0, 0.0],    # 3
                           [-0.7, -0.1, 0.0],   # 4
                           [0.0, -0.2, 0.05],   # 5
                           [-0.1, -0.65, 0.0],  # 6
                           [0.0, -0.75, 0.05],  # 7
                           [0.1, -0.65, 0.0],   # 8
                           [0.7, -0.1, 0.0],    # 9
                           [0.6, 0.0, 0.0],     # 10
                           [0.2, 0.1, 0.05],    # 11
                           [0.1, 0.1, 0.05],    # 12
                           [0.0, 0.2, 0.15],    # 13
                           [0.0, 0.0, 0.0],     # 14
                           ])

        self._patches = np.array([
            # Body:
            [points[0], points[1], points[13]],     # 0: head top left
            [points[12], points[0], points[13]],    # 1: head top right
            [points[1], points[5], points[13]],     # 2: back top left
            [points[5], points[12], points[13]],    # 3: back top right
            [points[1], points[0], points[14]],     # 4: head bottom left
            [points[0], points[12], points[14]],    # 5: head bottom right
            [points[5], points[1], points[14]],     # 6: back bottom left
            [points[12], points[5], points[14]],    # 7: back bottom right
            # Tail:
            [points[5], points[6], points[7]],      # 8: top left
            [points[8], points[5], points[7]],      # 9: top right
            [points[6], points[5], points[7]],      # 10: bottom left
            [points[5], points[8], points[7]],      # 11: bottom right
            # Left wing
            [points[1], points[2], points[5]],      # 12: inner top
            [points[2], points[3], points[5]],      # 13: middle top
            [points[3], points[4], points[5]],      # 14: tip top
            [points[2], points[1], points[5]],      # 15: inner bottom
            [points[3], points[2], points[5]],      # 16: middle bottom
            [points[4], points[3], points[5]],      # 17: tip bottom
            # Right wing
            [points[11], points[12], points[5]],    # 18: inner top
            [points[10], points[11], points[5]],    # 19: middle top
            [points[9], points[10], points[5]],     # 20: tip top
            [points[12], points[11], points[5]],    # 21: inner bottom
            [points[11], points[10], points[5]],    # 22: middle bottom
            [points[10], points[9], points[5]],     # 23: tip bottom
            ])

        self._colours = np.array([
            # Body:
            [0, 0, 0, 255],
            [0, 0, 0, 255],
            [0, 0, 26, 255],
            [0, 0, 26, 255],
            [204, 204, 204, 255],
            [204, 204, 204, 255],
            [0, 0, 0, 255],
            [0, 0, 0, 255],
            # Tail:
            [0, 26, 0, 255],
            [0, 26, 0, 255],
            [0, 13, 0, 255],
            [0, 13, 0, 255],
            # Left wing:
            [204, 204, 204, 255],
            [0, 13, 0, 255],
            [204, 204, 204, 255],
            [204, 204, 204, 255],
            [0, 0, 0, 255],
            [204, 204, 204, 255],
            # Right wing:
            [204, 204, 204, 255],
            [0, 13, 0, 255],
            [204, 204, 204, 255],
            [204, 204, 204, 255],
            [0, 0, 0, 255],
            [204, 204, 204, 255],
            ]) - 26

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

        self._scale = scale

        self._engine = np.array([0.0, 0.0, 0.0])

        self._gun = self.points[0]


class Lander(TriD):
    """
    Patches for Lander.
    """
    def __init__(self, basecolour=np.array([0, 204, 0, 255]),
                 position=np.array([0.0, 0.0, 0.0]),
                 yaw=0, pitch=0, roll=0, scale=1.0):
        points = np.array([[0.5, 1.0, 0.0],     # 0
                           [-0.5, 1.0, 0.0],    # 1
                           [-1.2, -0.1, 0.2],   # 2
                           [0.0, -1.0, 0.0],    # 3
                           [1.2, -0.1, 0.2],    # 4
                           [0.0, -0.4, 0.8],    # 5
                           [0.10, 0.2, 0.0],    # 6
                           [-.10, 0.2, 0.0],    # 7
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

        self._scale = scale

        self._engine = np.array([0.0, 0.0, 0.0])

        self._gun = np.array([0.0, 1.0, 0.0])


class House(TriD):
    """
    Patches for House with nicer shading and sorting properties than
    SimpleHouse, though twice as complex...
    """

    def __init__(self, basecolour=np.array([0, 204, 0, 255]),
                 position=np.array([0.0, 0.0, 0.0]),
                 yaw=0.0, pitch=0.0, roll=0.0, scale=1.0):
        points = np.array([[0.7, 1.2, 0.0],       # 0
                           [-0.7, 1.2, 0.0],      # 1
                           [-0.7, -1.2, 0.0],     # 2
                           [0.7, -1.2, 0.0],      # 3
                           [0.7, 1.2, 0.7],      # 4
                           [-0.7, 1.2, 0.7],     # 5
                           [-0.7, -1.2, 0.7],    # 6
                           [0.7, -1.2, 0.7],     # 7
                           [0.0, 1.2, 1.0],       # 8
                           [0.0, -1.2, 1.0],      # 9
                           ])

        self._patches = np.array([
            # North side:
            [points[0], points[1], points[(0, 1, 4, 5), :].mean(0)],  # bottom
            [points[5], points[4], points[(0, 1, 4, 5), :].mean(0)],  # middle
            [points[1], points[5], points[(0, 1, 4, 5), :].mean(0)],  # west
            [points[4], points[0], points[(0, 1, 4, 5), :].mean(0)],  # east
            [points[4], points[5], points[8]],                        # top
            # South side:
            [points[2], points[3], points[(2, 3, 6, 7), :].mean(0)],  # lower
            [points[7], points[6], points[(2, 3, 6, 7), :].mean(0)],  # middle
            [points[6], points[2], points[(2, 3, 6, 7), :].mean(0)],  # west
            [points[3], points[7], points[(2, 3, 6, 7), :].mean(0)],  # east
            [points[6], points[7], points[9]],                        # top
            # West side:
            [points[1], points[2], points[(1, 2, 5, 6), :].mean(0)],  # bottom
            [points[6], points[5], points[(1, 2, 5, 6), :].mean(0)],  # top
            [points[5], points[1], points[(1, 2, 5, 6), :].mean(0)],  # north
            [points[2], points[6], points[(1, 2, 5, 6), :].mean(0)],  # south
            # East side:
            [points[3], points[0], points[(0, 3, 4, 7), :].mean(0)],  # bottom
            [points[4], points[7], points[(0, 3, 4, 7), :].mean(0)],  # top
            [points[0], points[4], points[(0, 3, 4, 7), :].mean(0)],  # north
            [points[7], points[3], points[(0, 3, 4, 7), :].mean(0)],  # south
            # West roof:
            [points[5], points[6], points[(5, 6, 8, 9), :].mean(0)],  # bottom
            [points[9], points[8], points[(5, 6, 8, 9), :].mean(0)],  # top
            [points[8], points[5], points[(5, 6, 8, 9), :].mean(0)],  # north
            [points[6], points[9], points[(5, 6, 8, 9), :].mean(0)],  # south
            # East roof:
            [points[7], points[4], points[(4, 7, 8, 9), :].mean(0)],  # bottom
            [points[8], points[9], points[(4, 7, 8, 9), :].mean(0)],  # top
            [points[4], points[8], points[(4, 7, 8, 9), :].mean(0)],  # north
            [points[9], points[7], points[(4, 7, 8, 9), :].mean(0)],  # south
            ])

        self._colours = np.array([[153, 153, 102, 255],
                                  [153, 153, 102, 255],
                                  [153, 153, 102, 255],
                                  [153, 153, 102, 255],
                                  [153, 153, 102, 255],
                                  [153, 153, 102, 255],
                                  [153, 153, 102, 255],
                                  [153, 153, 102, 255],
                                  [153, 153, 102, 255],
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

        self._scale = scale


class SimpleHouse(TriD):
    """
    Patches for SimpleHouse with reduced triangle count. Probably a tiny bit
    faster to render than House.
    """

    def __init__(self, basecolour=np.array([0, 204, 0, 255]),
                 position=np.array([0.0, 0.0, 0.0]),
                 yaw=0.0, pitch=0.0, roll=0.0, scale=1.0):
        points = np.array([[0.7, 1.2, 0.0],       # 0
                           [-0.7, 1.2, 0.0],      # 1
                           [-0.7, -1.2, 0.0],     # 2
                           [0.7, -1.2, 0.0],      # 3
                           [0.7, 1.2, 0.7],      # 4
                           [-0.7, 1.2, 0.7],     # 5
                           [-0.7, -1.2, 0.7],    # 6
                           [0.7, -1.2, 0.7],     # 7
                           [0.0, 1.2, 1.0],       # 8
                           [0.0, -1.2, 1.0],      # 9
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

        self._scale = scale
