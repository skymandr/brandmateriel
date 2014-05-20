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

    X = U = 0
    Y = V = 1
    Z = W = 2

    def __init__(self, filename='demodata.npy', sealevel=0, flat_sea=True):
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
    def shape(self):
        return (self._raw_map.shape[1] - 1, self._raw_map.shape[0] - 1)

    @property
    def flat_sea(self):
        return self._flat_sea

    @property
    def raw_map(self):
        return self._raw_map

    def slice(self, position, view):
        xmin = np.round(position[self.X] - view[self.X] * 0.5).astype(np.int)
        xmax = np.round(position[self.X] + view[self.X] * 0.5).astype(np.int)
        ymin = np.round(position[self.Y] - view[self.Y] * 0.5).astype(np.int)
        ymax = np.round(position[self.Y] + view[self.Y] * 0.5).astype(np.int)

        Y, X = np.mgrid[ymin: ymax + 1, xmin: xmax + 1]

        X %= self.shape[self.X]
        Y %= self.shape[self.Y]

        return X, Y

    def patches_slice(self, position, view):
        """
        Returns a slice of the map patches centered on position, with
        dimensions decided by view.
        """

        X, Y = self.slice(position, view)

        xmin = position[self.X] - view[self.X] * 0.5
        xmax = position[self.X] + view[self.X] * 0.5
        ymin = position[self.Y] - view[self.Y] * 0.5
        ymax = position[self.Y] + view[self.Y] * 0.5

        the_slice = self._patches[X, Y, :]

        # Fix periodicity:
        the_slice = self.fix_view(position, view, the_slice)

        # Impose view limits:
        the_slice[:, 0, (3, 0), self.Z] += ((the_slice[:, 0, (2, 1), self.Z] -
                                            the_slice[:, 0, (3, 0), self.Z])
                                            * (xmin - the_slice[:, 0, (3, 0),
                                                                self.X]))

        the_slice[:, -1, (2, 1), self.Z] += ((the_slice[:, -1, (2, 1), self.Z]
                                              - the_slice[:, -1, (3, 0),
                                                          self.Z]) *
                                             (xmax - the_slice[:, -1, (2, 1),
                                                               self.X]))

        the_slice[0, :, (0, 1), self.Z] += ((the_slice[0, :, (3, 2), self.Z] -
                                             the_slice[0, :, (0, 1), self.Z])
                                            * (ymin - the_slice[0, :, (0, 1),
                                                                self.Y]))

        the_slice[-1, :, (3, 2), self.Z] += ((the_slice[-1, :, (3, 2), self.Z]
                                              - the_slice[-1, :, (0, 1),
                                                          self.Z]) *
                                             (ymax - the_slice[-1, :, (3, 2),
                                                               self.Y]))

        the_slice[:, 0, (3, 0), self.X] = xmin
        the_slice[:, -1, (1, 2), self.X] = xmax
        the_slice[0, :, (0, 1), self.Y] = ymin
        the_slice[-1, :, (2, 3), self.Y] = ymax

        return the_slice

    def map_positions_slice(self, position, view):
        """
        Returns a slice of the map positions centered on position, with
        dimensions decided by view.
        """

        X, Y = self.slice(position, view)

        the_slice = self._positions[X, Y, :]

        # Fix periodicity:
        the_slice = self.fix_view(position, view, the_slice)

        return the_slice

    def patch_positions_slice(self, position, view):
        """
        Returns a slice of the patch positions centered on position, with
        dimensions decided by view.
        """

        X, Y = self.slice(position, view)

        the_slice = self._positions[X, Y, :]

        # Fix periodicity:
        the_slice = self.fix_view(position, view, the_slice)

        return the_slice

    def normals_slice(self, position, view):
        """
        Returns a slice of the map normals centered on position, with
        dimensions decided by view.
        """

        X, Y = self.slice(position, view)

        return self._normals[X, Y, :]

    def colours_slice(self, position, view):
        """
        Returns a slice of the map colours centered on position, with
        dimensions decided by view.
        """

        X, Y = self.slice(position, view)

        return self._colours[X, Y, :]

    def patches_list(self, position, view):
        """
        Returns patches as a list for use in Camera etc.
        """

        the_slice = self.patches_slice(position, view)
        size = the_slice.shape[0] * the_slice.shape[1]

        return the_slice.reshape((size, 4, 3))

    def map_positions_list(self, position, view):
        """
        Returns positions as a list for use in Camera etc.
        """

        the_slice = self.map_positions_slice(position, view)
        size = the_slice.shape[0] * the_slice.shape[1]

        return the_slice.reshape((size, 3))

    def patch_positions_list(self, position, view):
        """
        Returns positions as a list for use in Camera etc.
        """

        the_slice = self.patch_positions_slice(position, view)
        size = the_slice.shape[0] * the_slice.shape[1]

        return the_slice.reshape((size, 3))

    def normals_list(self, position, view):
        """
        Returns normals as a list for use in Camera etc.
        """
        the_slice = self.normals_slice(position, view)
        size = the_slice.shape[0] * the_slice.shape[1]

        return the_slice.reshape((size, 3))

    def colours_list(self, position, view):
        """
        Returns colours as a list for use in Camera etc.
        """
        the_slice = self.colours_slice(position, view)
        size = the_slice.shape[0] * the_slice.shape[1]

        return the_slice.reshape((size, 4))

    @property
    def patches(self):
        """
        Returns patches in native shape.
        """

        return self._patches

    @property
    def map_positions(self):
        """
        Returns positions in native shape.
        """

        return self._positions

    @property
    def patch_positions(self):
        """
        Returns positions in native shape.
        """

        return self._positions

    @property
    def normals(self):
        """
        Returns normals in native shape.
        """
        return self._normals

    @property
    def colours(self):
        """
        Returns colours in native shape.
        """
        return self._colours

    def fix_view(self, position, view, positions):
        xmin = position[self.X] - view[self.X] * 0.5
        xmax = position[self.X] + view[self.X] * 0.5
        ymin = position[self.Y] - view[self.Y] * 0.5
        ymax = position[self.Y] + view[self.Y] * 0.5

        # Fix periodicity:
        if xmin <= 0.0:

            positions[..., self.X] = ((positions[..., self.X] +
                                       view[self.X] * 0.5 + 0.5) %
                                      self.shape[self.X] -
                                      view[self.X] * 0.5 - 0.5)

        elif xmax >= self.shape[self.X] - 1.0:

            positions[..., self.X] = ((positions[..., self.X] -
                                       view[self.X] * 0.5 - 1.0) %
                                      self.shape[self.X] +
                                      view[self.X] * 0.5 + 1.0)

        if ymin <= 0.0:

            positions[..., self.Y] = ((positions[..., self.Y] +
                                       view[self.Y] * 0.5 + 0.5) %
                                      self.shape[self.Y] -
                                      view[self.Y] * 0.5 - 0.5)

        elif ymax >= self.shape[self.Y] - 1.0:

            positions[..., self.Y] = ((positions[..., self.Y] -
                                       view[self.Y] * 0.5 - 1.0) %
                                      self.shape[self.Y] +
                                      view[self.Y] * 0.5 + 1.0)
        return positions

    def positions_in_view(self, position, view, positions):
        xmin = position[self.X] - view[self.X] * 0.5
        xmax = position[self.X] + view[self.X] * 0.5
        ymin = position[self.Y] - view[self.Y] * 0.5
        ymax = position[self.Y] + view[self.Y] * 0.5

        return np.where((positions[:, self.X] >= xmin) *
                        (positions[:, self.X] <= xmax) *
                        (positions[:, self.Y] >= ymin) *
                        (positions[:, self.Y] <= ymax))[0]

    def _make_patches(self):
        """
        Create patches made up of four points (corners of squares in the
        xy-plane).
        """

        # Ininitalise patches:
        xsize, ysize = self.shape
        patches = np.zeros((xsize, ysize, 4, 3))

        # Fill patches:
        # These for-loops could be removed:
        for x in xrange(xsize):
            for y in xrange(ysize):
                xinds = np.array([x, x + 1, x + 1, x])
                yinds = np.array([y, y, y + 1, y + 1])
                patches[x, y, :, 0] = xinds - 0.5
                patches[x, y, :, 1] = yinds - 0.5
                patches[x, y, :, 2] = self.raw_map[yinds, xsize - xinds]

        self._patches = patches

    def _colourise(self):
        """
        Not yet fully implemented, but should assign colours (with some sort of
        noise) to patches.

        Currently debug wit just green and blue.
        """
        colours = np.zeros([self._patches.shape[0], self._patches.shape[1], 4],
                           dtype=np.int)

        max_height = self._positions[:, :, self.Z].max()
        for x in xrange(colours.shape[self.X]):
            for y in xrange(colours.shape[self.Y]):
                height = self._positions[x, y, self.Z]
                if height > self.sealevel:
                    colours[x, y] = np.array([51, 102, 26, 255]) + np.array(
                        [np.random.random() * height / max_height,
                         np.random.random() * (1 - height / max_height),
                         0, 0]) * 153
                else:
                    colours[x, y] = np.array([0, 0, 77, 255])

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

        v0s = self._patches[:, :, 1] - self._patches[:, :, 0]
        v1s = self._patches[:, :, 2] - self._patches[:, :, 1]
        v2s = self._patches[:, :, 3] - self._patches[:, :, 2]
        v3s = self._patches[:, :, 0] - self._patches[:, :, 3]

        normals = np.cross(v0s, v1s + v3s) + np.cross(v2s, v3s - v1s)
        normals /= np.sqrt((normals ** 2).sum(-1))[:, :, np.newaxis]

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


class TriMap(object):
    """
    NOT UP TO DATE!
    The Map class contains data for displaying/rendering a map of an area.

    The data is:
    * patches:
        - sets of four triangular patches that are the units of the map

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

    X = U = 0
    Y = V = 1
    Z = W = 2

    def __init__(self, filename='demodata.npy', sealevel=0, flat_sea=True):
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
    def shape(self):
        return (self._raw_map.shape[1] - 1, self._raw_map.shape[0] - 1)

    @property
    def flat_sea(self):
        return self._flat_sea

    @property
    def raw_map(self):
        return self._raw_map

    def slice(self, position, view):
        the_position = np.round(position).astype(np.int)

        Y, X = np.mgrid[the_position[self.Y] - view[self.Y] / 2 - 1:
                        the_position[self.Y] + view[self.Y] / 2 + 1,
                        the_position[self.X] - view[self.X] / 2 - 1:
                        the_position[self.X] + view[self.X] / 2 + 1]

        X %= self.shape[self.X]
        Y %= self.shape[self.Y]

        return X, Y

    def patches_slice(self, position, view):
        """
        Returns a slice of the map patches centered on position, with
        dimensions decided by view.
        """

        X, Y = self.slice(position, view)

        return self._patches[X, Y, :]

    def patch_positions_slice(self, position, view):
        """
        Returns a slice of the patch positions centered on position, with
        dimensions decided by view.
        """

        X, Y = self.slice(position, view)

        return self._patch_positions[X, Y, :]

    def map_positions_slice(self, position, view):
        """
        Returns a slice of the map positions centered on position, with
        dimensions decided by view.
        """

        X, Y = self.slice(position, view)

        return self._map_positions[X, Y, :]

    def normals_slice(self, position, view):
        """
        Returns a slice of the map normals centered on position, with
        dimensions decided by view.
        """

        X, Y = self.slice(position, view)

        return self._normals[X, Y, :]

    def colours_slice(self, position, view):
        """
        Returns a slice of the map colours centered on position, with
        dimensions decided by view.
        """

        X, Y = self.slice(position, view)

        return self._colours[X, Y, :]

    def patches_list(self, position, view):
        """
        Returns patches as a list for use in Camera etc.
        """

        the_slice = self.patches_slice(position, view)
        size = the_slice.shape[0] * the_slice.shape[1]

        return the_slice.reshape((size * 4, 3, 3))

    def map_positions_list(self, position, view):
        """
        Returns map positions as a list for use in Camera etc.
        """

        the_slice = self.map_positions_slice(position, view)
        size = the_slice.shape[0] * the_slice.shape[1]

        return the_slice.reshape((size, 3))

    def patch_positions_list(self, position, view):
        """
        Returns patch positions as a list for use in Camera etc.
        """

        the_slice = self.patch_positions_slice(position, view)
        size = the_slice.shape[0] * the_slice.shape[1]

        return the_slice.reshape((size * 4, 3))

    def normals_list(self, position, view):
        """
        Returns normals as a list for use in Camera etc.
        """
        the_slice = self.normals_slice(position, view)
        size = the_slice.shape[0] * the_slice.shape[1]

        return the_slice.reshape((size * 4, 3))

    def colours_list(self, position, view):
        """
        Returns colours as a list for use in Camera etc.
        """
        the_slice = self.colours_slice(position, view)
        size = the_slice.shape[0] * the_slice.shape[1]

        return the_slice.reshape((size * 4, 4))

    @property
    def patches(self):
        """
        Returns patches in native shape.
        """

        return self._patches

    @property
    def map_positions(self):
        """
        Returns positions in native shape.
        """

        return self._map_positions

    @property
    def patch_positions(self):
        """
        Returns positions in native shape.
        """

        return self._patch_positions

    @property
    def normals(self):
        """
        Returns normals in native shape.
        """
        return self._normals

    @property
    def colours(self):
        """
        Returns colours in native shape.
        """
        return self._colours

    def _make_patches(self):
        """
        Create patches made up of three points, dividing the squares into four
        triangles.
        """

        # Ininitalise patches:
        xsize, ysize = self.shape
        patches = np.zeros((xsize, ysize, 4, 3, 3))

        # Fill patches:
        # This for-looops could and should be removed:
        for x in xrange(xsize):
            for y in xrange(ysize):
                xinds = np.array([x, x + 1, x + 1, x, x])
                yinds = np.array([y, y, y + 1, y + 1, y])
                xcentre = xinds[: 4].mean() - 0.5
                ycentre = yinds[: 4].mean() - 0.5
                zcentre = self.raw_map[yinds, xsize - xinds].mean()
                for n in xrange(4):
                    patches[x, y, n, :, 0] = np.r_[xinds[n: n + 2] - 0.5,
                                                   xcentre]
                    patches[x, y, n, :, 1] = np.r_[yinds[n: n + 2] - 0.5,
                                                   ycentre]
                    patches[x, y, n, :, 2] = np.r_[self.raw_map[
                        yinds[n: n + 2], xsize - xinds[n: n + 2]], zcentre]

        self._patches = patches

    def _colourise(self):
        """
        Not yet fully implemented, but should assign colours (with some sort of
        noise) to patches.

        Currently debug wit just green and blue.
        """
        colours = np.zeros([self._patches.shape[0], self._patches.shape[1], 4,
                            4], dtype=np.int)

        for x in xrange(colours.shape[0]):
            for y in xrange(colours.shape[1]):
                if self._map_positions[x, y, 2] > self.sealevel:
                    colours[x, y, :] = np.array([102, 153, 0, 255])
                else:
                    colours[x, y, :] = np.array([0, 0, 77, 255])

        self._colours = colours

    def _calc_positions(self):
        """
        Useful for sorting and the like.
        """

        self._patch_positions = self._patches.mean(3)
        self._map_positions = self._patch_positions.mean(2)

    def _calc_normals(self):
        """
        This is a little bit arbitrary since the normal is not well defined
        for patches, but it is arbitrary in a very systematic way and therefore
        gives a nice noise effect (hopefully).
        """

        normals = np.zeros([self._patches.shape[0], self._patches.shape[1], 4,
                            3])

        v0s = self._patches[:, :, :, 1] - self._patches[:, :, :, 0]
        v1s = self._patches[:, :, :, 2] - self._patches[:, :, :, 1]

        normals = np.cross(v0s, v1s)
        normals /= np.sqrt((normals ** 2).sum(-1))[:, :, :, np.newaxis]

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

        self._patches[:, :, :, :, 2] = np.where(
            self._patches[:, :, :, :, 2] < self.sealevel, self.sealevel,
            self._patches[:, :, :, :, 2])

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
