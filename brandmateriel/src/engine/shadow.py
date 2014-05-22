import numpy as np

X = U = 0
Y = V = 1
Z = W = 2


def get_shadows(patches, world):
    """
    Function for getting shadow of object on ground.

    The patches Z assigment could benefit from tweaking (weighted mean of
    map tile heights feasible?), but more than that, drawing the thing
    is really very difficult, since maptiles drawn after the shadowpatches,
    can be drawn over the shadow...

    The shadows could also benefit from having their normals defined, so that
    they can be culled under extreme circumstances. This would be easy.
    Getting the draworder to work is hard...
    """

    positions = patches.mean(-2)

    # positions[..., Z] = patches[..., Z].max()

    # positions[..., Y] = patches[..., Y].min()

    positions[..., Z] = np.where(positions[..., Z] < 0, 0, positions[..., Z])

    patches[..., Z] = world.patch_positions[patches[..., X].astype(np.int),
                                            patches[..., Y].astype(np.int),
                                            Z]
    patches[..., Z] = np.where(patches[..., Z] < 0, 0, patches[..., Z])

    """
    positions = patches.mean(-2)

    positions[..., Z] = world.patches[positions[..., X].astype(np.int),
                                      positions[..., Y].astype(np.int),
                                      :, Z].max(-1)

    positions[..., Z] = np.where(positions[..., Z] < 0, 0, positions[..., Z])

    positions[..., Y] = patches[..., Y].min()
    """

    return patches, positions
