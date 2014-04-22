import numpy as np


class Map(object):
    """
    The Map class contains data for displaying/rendering a map of an area.

    The data is:
    * patches:
        - semi-rectangular patches that are the units of the map

    * positions:
        - positions of the patches, calculated as the man of the patches'
          corner positions.

    * normals:
        - an approximation of the normal to the patches, useful for shading.

    * sealevel:
        - a minimum level, under witch patches will not extend.

    * colours:
        - per-patch colour triplet, randomly assigned based on distance to
          sealevel and such.
    """

    def __init__(self, filename='demodata.npy', sealevel=0, flat_sea=False):
        if filename is None:
            self._raw_map = np.zeros([10, 13])
        else:
            self._raw_map = np.load(filename)

        self._sealevel = sealevel

        self._flat_sea = flat_sea

        self._make_patches()

        self._size = self._patches.size / 12

        self._calc_positions()

        if self._flat_sea:
            self._flood()

        self._calc_normals()

        self._colourise()

        if not self._flat_sea:
            self._flood()

    @property
    def sealevel(self):
        return self._sealevel

    @property
    def flat_sea(self):
        return self._flat_sea

    @property
    def raw_map(self):
        return self._raw_map

    @property
    def patches(self):
        return self._patches.reshape((self._size, 4, 3))

    @property
    def normals(self):
        return self._normals.reshape((self._size, 3))

    @property
    def positions(self):
        return self._positions.reshape((self._size, 3))

    @property
    def colours(self):
        return self._colours.reshape((self._size, 3))

    def _make_patches(self):
        """
        Create patches made up of four points (corners of squares in the
        xy-plane).
        """

        # Ininitalise patches:
        patches = np.zeros((self.raw_map.shape[1] - 1,
                            self.raw_map.shape[0] - 1, 4, 3))

        # Fill patches:
        # This for-looops could and should be removed:
        for x in xrange(patches.shape[0]):
            for y in xrange(patches.shape[1]):
                xinds = [x, x + 1, x + 1, x]
                yinds = [y, y, y + 1, y + 1]
                patches[x, y, :, 0] = np.array(xinds) - 0.5
                patches[x, y, :, 1] = np.array(yinds) - 0.5
                patches[x, y, :, 2] = self.raw_map[yinds, xinds]

        self._patches = patches

    def _colourise(self):
        """
        Not yet fully implemented, but should assign colours (with some sort of
        noise) to patches.

        Currently debug wit just green and blue.
        """
        colours = np.zeros([self._patches.shape[0], self._patches.shape[1], 3],
                           dtype=np.int)

        RED = np.array((153, 0, 0))
        GREEN = np.array((0, 153, 0))
        BLUE = np.array((0, 0, 153))

        for x in xrange(colours.shape[0]):
            for y in xrange(colours.shape[1]):
                if self._positions[x, y, 2] > self.sealevel:
                    colours[x, y] = 0 * RED + 1 * GREEN + 0 * BLUE
                else:
                    colours[x, y] = 0 * RED + 0 * GREEN + 1 * BLUE

        self._colours = colours

    def _calc_positions(self):
        """
        Useful for sorting and the like.
        """

        self._positions = self._patches.mean(2)

    def _calc_normals(self):
        """
        This is a little bit arbitrary since the normal is not well defined
        for patches, but it is arbitrary in a very systematic way and therefore
        gives a nice noise effect (hopefully).
        """

        normals = np.zeros([self._patches.shape[0], self._patches.shape[1], 3])

        # This for-loops probably could and should be removed:
        for x in xrange(normals.shape[0]):
            for y in xrange(normals.shape[1]):
                v0 = self._patches[x, y, 1] - self._patches[x, y, 0]
                v1 = self._patches[x, y, 2] - self._patches[x, y, 1]
                v2 = self._patches[x, y, 3] - self._patches[x, y, 2]
                v3 = self._patches[x, y, 0] - self._patches[x, y, 3]

                # normals[x, y] = np.cross(v0 + v1, -v0 - v3)
                # normals[x, y] /= np.linalg.norm(normals[x, y])

                normals[x, y] = np.cross(v0, v1 + v3) + np.cross(v2, v3 - v1)
                normals[x, y] /= np.linalg.norm(normals[x, y])

        self._normals = normals

    def _flood(self):
        """
        Raises patch-points that are under the sealevel to the sealevel to
        ensure a flat sea.

        If run after calc_normals(), this should give an interesting shading
        effect.

        If run after calc_positions() it opens for the opportunity of going
        under water some time in the future, and gives "breaking waves"
        on shores.
        """

        self._patches[:, :, :, 2] = np.where(
            self._patches[:, :, :, 2] < self.sealevel, self.sealevel,
            self._patches[:, :, :, 2])

    def reflood(self, sealevel, flat_sea=False):
        self._sealevel = sealevel

        self._flat_sea = flat_sea

        self._make_patches()

        self._calc_positions()

        if self.flat_sea:
            self._flood()

        self._calc_normals()

        self._colourise()

        if not self.flat_sea:
            self._flood()
