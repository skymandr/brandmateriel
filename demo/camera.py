import numpy as np


class Screen(object):
    """
    A Screen object for use with a Camera object.

    The Screen is described by the following parameters:
    * extent:
        - the Screen's extent (width, height) in spatial units

    * resolution:
        - the Screen's resoultion in pixels (xres, yres)

    * position:
        - position of the centre of the Screen in uvw-space, using the Camera
          position as origin.
          The v component is the proper orthogonalvdistance to the Screen from
          the Camera.
    """

    X = U = 0
    Y = V = 1
    Z = W = 2

    def __init__(self,
                 extent=np.array([12.0, 9.0]), resolution=np.array([320, 240]),
                 position=np.array([0.0, 9.0, -1.5])):

        self.position = position

        self.extent = extent

        self.resolution = resolution

    @property
    def position(self):
        return self._position

    @position.setter
    def position(self, val):
        self._position = val

    @property
    def extent(self):
        return self._extent

    @extent.setter
    def extent(self, val):
        self._extent = val

    @property
    def resolution(self):
        return self._resolution

    @resolution.setter
    def resolution(self, val):
        self._resolution = val

    @property
    def u(self):
        return self._position[self.U]

    @u.setter
    def u(self, val):
        self._position[self.U] = val

    @property
    def v(self):
        return self._position[self.V]

    @v.setter
    def v(self, val):
        self._position[self.V] = val

    @property
    def w(self):
        return self._position[self.W]

    @w.setter
    def w(self, val):
        self._position[self.W] = val

    @property
    def width(self):
        return self._extent[self.X]

    @property
    def height(self):
        return self._extent[self.Y]

    @property
    def distance(self):
        return self._position[self.V]

    @property
    def xres(self):
        return self._resolution[self.X]

    @property
    def yres(self):
        return self._resolution[self.Y]


class Camera(object):
    """
    A simple Camera object.

    The Camera are defined by the following parameters:
    * position:
        - one vector describing the position of the Camera in xyz-space.

    * orientation:
        - a set of three orthogonal unit vectors (u, v, w) analogous to and
          expressed in the (x, y, z) set of unit vectors and using the same
          metric/normalisation.
          Of these, the u and w vectors describe the orientation of the Screen
          relative to the Camera ("roll" and "elevation") and v points
          in the viewing direction.

    * screen:
        - the screen is described by its extent (width, height) in spatial
          units, by its resolution in pixels (xres, yres), and by the position
          of the centre of in uvw-space using the Camera position as
          origin.
          The v component is the proper orthogonal distance to the Screen from
          the Camera.
          See the Screen class for details!

    The Camera has the following methods:
    * get_screen_coordinates(points):
        - returns the screen coordinate of points (an N x 3-array of positions
          in xyz-space) based on current Camera position and orientation.

    * look_at_point(point):
        - turn camera to look at point, keeping position and roll constant.

    * get_azimuthl():
        - returns current azimuthal angle (angle to x-axis) of Camera
          orientation.

    * get_elevation():
        - returns current elevation angle (angle to xy-plane) of Camera
          orientation

    * get_roll():
        - returns current roll angle (rotation around v-axis) of Camera
          orientation.
    """

    X = U = 0
    Y = V = 1
    Z = W = 2

    def __init__(self,
                 position=np.array([6.0, -9.0, 6.0]),
                 orientation=np.array([[1.0, 0.0, 0.0],     # u
                                       [0.0, 1.0, 0.0],     # v
                                       [0.0, 0.0, 1.0]]),   # w
                 screen=Screen()):

        self.position = position

        self.orientation = orientation

        self.screen = screen
        self._norms = self.screen.resolution / self.screen.extent

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
    def screen(self):
        return self._screen

    @screen.setter
    def screen(self, val):
        self._screen = val

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

    def get_screen_coordinates(self, points):
        # Perform projections:
        projections = np.inner(points.reshape(points.size / 3, 3) -
                               self.position, self.orientation)

        # Rescale to screen distance:
        projections *= np.abs(self.screen.distance /
                              projections[:, np.newaxis, 1])

        # Change origin to upper-left corner of screen:
        projections += np.array([self.screen.width * 0.5 - self.screen.u,
                                0.0, -self.screen.height * 0.5 -
                                self.screen.w])

        # Convert to left-handed pixel space and return:
        return np.round(np.array(
                        [projections[:, self.U] * self._norms[self.X],
                         -projections[:, self.W] * self._norms[self.Y]]
                        ).T).astype(np.int)

    def look_at_point(self, point):
        roll = self.get_roll()

        delta = point - self.position
        v = delta / np.linalg.norm(delta)
        u = np.cross(v, np.array([0.0, 0.0, 1.0]))
        u /= np.linalg.norm(u)
        w = np.cross(u, v)

        # This is clumsy:
        self.orientation = np.c_[u, v, w].T

        # This is not implemented:
        self.set_roll(roll)

    def get_azimuth(self):
        return np.arctan2(self.v[self.Y], self.v[self.X])

    def get_elevation(self):
        return np.arcsin(self.v[self.W])

    def get_roll(self):
        u = np.cross(self.v, np.array([0.0, 0.0, 1.0]))

        return np.arctan2(np.dot(self.v, np.cross(u, self.u)),
                          np.dot(u, self.u))

    def set_roll(self, roll):
        print "Sorry! set_roll() is not yet implemented.!"
