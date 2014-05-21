import numpy as np

X = U = 0
Y = V = 1
Z = W = 2


def get_shadows(patches, positions, world):
    patches[..., Z] = world.patch_positions[patches[..., X].astype(np.int),
                                              patches[..., Y].astype(np.int),
                                              Z]
    patches[..., Z] = np.where(patches[..., Z] < 0, 0, patches[..., Z])

    positions[..., Z] = world.map_positions[positions[..., X].astype(np.int),
                                            positions[..., Y].astype(np.int),
                                            Z]
    positions[..., Z] = np.where(positions[..., Z] < 0, 0, positions[..., Z])

    print positions[..., Z]

    return patches, positions
