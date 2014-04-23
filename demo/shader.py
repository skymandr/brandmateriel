import numpy as np


class LightSource(object):
    """
    This object has a position (and orientation) for the light source.

    For many applications, using the Camera as a light source is probably what
    is desired.
    """

    X = U = 0
    Y = V = 1
    Z = W = 2

    def __init__(self,
                 position=np.array([6.0, -9.0, 6.0]),
                 orientation=np.array([[1.0, 0.0, 0.0],     # u
                                       [0.0, 1.0, 0.0],     # v
                                       [0.0, 0.0, 1.0]])):  # w
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


class Shader(object):
    """
    The Shader applies shading to patches, based on the orienation of the
    patches' normals to the light-source.

    Currently, only the position of the light source matters, but there is at
    least a skeleton for implementing light directionality and such at a later
    stage. The standard Camera object can be used as a light source, unless
    a fixed light source is desired.
    """

    def __init__(self, light_source=LightSource(),
                 colour=np.array([255, 255, 255, 255])):
        self._light_source = light_source
        self._colour = colour

    @property
    def light_source(self):
        return self._light_source

    @light_source.setter
    def light_source(self, val):
        self._light_source = val

    @property
    def colour(self):
        return self._colour

    @colour.setter
    def colour(self, val):
        self._colour = val

    def apply_lighting(self, positions, normals, colours):
        """
        Questions:
            this is done explicitly by reference, changing original colours;
            is that good or annoying?
        """
        Deltas = positions - self.light_source.position
        Deltas /= np.sqrt((Deltas ** 2).sum(-1))[:, np.newaxis]

        scatter = (Deltas * normals).sum(-1)
        colours -= self.colour * scatter[:, np.newaxis]
        colours = np.where(colours > 255, 255, colours)
        colours = np.where(colours < 0, 0, colours)
        colours[:, 3] = 255
        colours[np.where(scatter > 0), 3] = 0

        return colours
