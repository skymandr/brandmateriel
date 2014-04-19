import numpy as np

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

    def __init__(self,
                 position=np.array([6.0, -9.0, 6.0]),
                 orientation=np.array([[1.0, 0.0, 0.0],     # u
                                       [0.0, 1.0, 0.0],     # v
                                       [0.0, 0.0, 1.0]]),   # w
                 extent=np.array([12.0, 9.0]), resolution=np.array([320, 240]),
                 screen_position=np.array([0.0, 9.0, -1.5]), mpldebug=False):

        self.position = position
        # These should not be instantiated, and only be accessed using Xetters:
        self.x = position[0]
        self.y = position[1]
        self.z = position[2]

        self.orientation = orientation
        # These should not be instantiated, and only be accessed using Xetters:
        self.u = orientation[0]
        self.v = orientation[1]
        self.w = orientation[2]

        self.screen = Screen(extent, resolution, screen_position)
        self._norms = self.screen.resolution / self.screen.extent

        self.mpldebug = mpldebug

    def get_screen_coordinates(self, points):
        # Perform projections:
        projections = np.inner(points.reshape(points.size / 3, 3) -
                             self.position, self.orientation)

        # Rescale to screen distance:
        projections *= np.abs(self.screen.distance /
                              projections[:, np.newaxis, 1])

        if self.mpldebug:
            # Change origin to lower-left corner of screen:
            projections += np.array([self.screen.width * 0.5 - self.screen.u,
                                    0.0, self.screen.height * 0.5 -
                                    self.screen.w])

            # Convert to pixel space and return:
            return np.array([projections[:, 0] * self._norms[0],
                             projections[:, 2] * self._norms[1]])
        else:
            # Change origin to upper-left corner of screen:
            projections += np.array([self.screen.width * 0.5 - self.screen.u,
                                    0.0, -self.screen.height * 0.5 -
                                    self.screen.w])

            # Convert to left-handed pixel space and return:
            return np.array([ projections[:, 0] * self._norms[0],
                             -projections[:, 2] * self._norms[1]])

    def look_at_point(self, point):
        roll = self.get_roll()

        delta = point - self.position
        v = delta / np.linalg.norm(delta)
        u = np.cross(v, np.array([0.0, 0.0, 1.0]))
        u /= np.linalg.norm(u)
        w = np.cross(u, v)

        # This is clumsy:
        self.orientation = np.c_[u, v, w].T
        # Or rather, this is:
        self.u = u
        self.v = v
        self.w = w

        # This is not implemented:
        self.set_roll(roll)

    def get_azimuth(self):
        return np.arctan2(self.v[1], self.v[0])

    def get_elevation(self):
        return np.arcsin(self.v[2])

    def get_roll(self):
        u = np.cross(self.v, np.array([0.0, 0.0, 1.0]))

        return np.arctan2(np.dot(self.v, np.cross(u, self.u)),
                          np.dot(u, self.u))

    def set_roll(self, roll):
        print "Sorry! set_roll() is not yet implemented.!"


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

    def __init__(self,
                 extent=np.array([12.0, 9.0]), resolution=np.array([320, 240]),
                 position=np.array([0.0, 9.0, -1.5])):

        self.position = position
        # These should not be instantiated, and only be accessed using Xetters:
        self.u = position[0]
        self.v = position[1]
        self.w = position[2]

        self.extent=extent
        # These should not be instantiated, and only be accessed using Xetters:
        self.width = extent[0]
        self.height = extent[1]
        self.distance = position[1]

        self.resolution = resolution
        # These should not be instantiated, and only be accessed using Xetters:
        self.xres = resolution[0]
        self.yres = resolution[1]
