import numpy as np


def apply_shading(points, normals, colours, lightsource):
    pass


class LightSource(object):
    """
    This object has a position (and direction) for the light source.

    For many applications, using the Camera as a light source is probably what
    is desired.
    """

    X = U = 0
    Y = V = 1
    Z = W = 2

    def __init__(self, position, orientation):
        self.position = position

        self.orientation = orientation

    @property
    def position(self):
        return self._position

    @position.setter
    def position(self, val):
        self._position = val

    @property
    def orientation(self):
        return self._orientation

    @orientation.setter
    def orientation(self, val):
        self._orientation = val

    @property
    def x(self):
        return self._position[self.X]

    @x.setter
    def x(self, val):
        self._position[self.X] = val

    @property
    def y(self):
        return self._position[self.Y]

    @y.setter
    def y(self, val):
        self._position[self.Y] = val

    @property
    def z(self):
        return self._position[self.Z]

    @z.setter
    def z(self, val):
        self._position[self.Z] = val

    @property
    def u(self):
        return self._orientation[self.U]

    @u.setter
    def u(self, val):
        self._orientation[self.U] = val

    @property
    def v(self):
        return self._orientation[self.V]

    @v.setter
    def v(self, val):
        self._orientation[self.V] = val

    @property
    def w(self):
        return self._orientation[self.W]

    @w.setter
    def w(self, val):
        self._orientation[self.W] = val
