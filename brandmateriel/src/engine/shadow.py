import numpy as np

X = U = 0
Y = V = 1
Z = W = 2


def get_shadows(patches, world):
    """
    Function for getting shadow of object on ground.

    Patch-Z assignment could do with tweaking.
    """

    positions = patches.mean(-2)

    positions[..., Z] = np.where(positions[..., Z] < 0, 0, positions[..., Z])
    xind = patches[..., X].astype(np.int) % world.shape[X]
    yind = patches[..., Y].astype(np.int) % world.shape[Y]

    # This needs to be made more accurate
    dists2 = ((patches[..., np.newaxis, : Z] -
               world.patches[xind, yind, :, : Z]) ** 2).sum(-1)
    patches[..., Z] = (world.patches[xind, yind, :, Z]
                       / dists2).sum(-1) / (1 / dists2).sum(-1) - 0.0125
    patches[..., Z] = np.where(patches[..., Z] < 0, 0, patches[..., Z])

    return patches, positions


def get_small_shadows(patches, world):
    """
    Function for getting shadow of smaller object on ground.

    Simplified Z assignment for small objects
    """

    positions = patches.mean(-2)

    positions[..., Z] = np.where(positions[..., Z] < 0, 0, positions[..., Z])
    xind = patches[..., X].astype(np.int) % world.shape[X]
    yind = patches[..., Y].astype(np.int) % world.shape[Y]

    patches[..., Z] = (world.map_positions[xind, yind, Z].mean(-1)
                       )[:, np.newaxis]
    patches[..., Z] = np.where(patches[..., Z] < 0, 0, patches[..., Z])

    return patches, positions
