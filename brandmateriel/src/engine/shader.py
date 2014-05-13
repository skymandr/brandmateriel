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
                                       [0.0, 0.0, 1.0]]),   # w
                 distance=9):
        self._position = position

        self._orientation = orientation

        self._distance = distance

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
    def distance(self):
        return self._distance

    @distance.setter
    def distance(self, val):
        self._distance = val

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

    X = U = 0
    Y = V = 1
    Z = W = 2

    def __init__(self, light_source=LightSource(),
                 colour=np.array([204, 153, 153, 255]),
                 distance_shading=True, cutoff_distance=None):
        self._light_source = light_source

        self._colour = colour

        self._distance_shading = distance_shading

        if cutoff_distance is None:
            self._cutoff_distance = self.light_source.distance
        else:
            self._cutoff_distance = cutoff_distance

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

    @property
    def distance_shading(self):
        return self._distance_shading

    @distance_shading.setter
    def distance_shading(self, val):
        self._distance_shading = val

    @property
    def cutoff_distance(self):
        return self._cutoff_distance

    @cutoff_distance.setter
    def cutoff_distance(self, val):
        self._cutoff_distance = val

    def apply_lighting(self, positions, normals, colours, culling=True):
        """
        Questions:
            this is done explicitly by reference, changing original colours;
            is that good or annoying?
        """
        deltas = positions - self.light_source.position
        dists = np.sqrt((deltas ** 2).sum(-1))[:, np.newaxis]
        deltas /= dists

        # Apply scatter:
        scatter = (deltas * normals).sum(-1)
        colours -= self.colour * scatter[:, np.newaxis]

        # Apply distance shading:
        if self.distance_shading:
            # Gauss:
            # colours *= np.exp(-(dists - self.cutoff_distance) ** 2 /
            #                  (4 * self.cutoff_distance ** 2))
            # Logistic:
            # colours /= 1 + 0.5 * np.exp(dists - 2 * self.cutoff_distance)
            # Linear with cut-off: (LinRange - dists + ConstRange) / LinRange
            colours *= np.fmin(1, np.fmax(0,
                                          (2 * self.cutoff_distance - dists)
                                          / (1 * self.cutoff_distance)))

        # Renormalise to allowed colour values:
        colours = np.where(colours > 255, 255, colours)
        colours = np.where(colours < 0, 0, colours)
        colours[:, 3] = 255
        if culling:
            colours[np.where(scatter > 0), 3] = 0

        return colours
