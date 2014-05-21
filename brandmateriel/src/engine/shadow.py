import numpy as np

X = U = 0
Y = V = 1
Z = W = 2


def get_shadows(patches, world):
    patches[..., Z] = world.patch_positions[patches[..., X].astype(np.int),
                                              patches[..., Y].astype(np.int),
                                              Z] + 0.01
    patches[..., Z] = np.where(patches[..., Z] < 0, 0, patches[..., Z]) + 0.01

    return patches, patches.mean(-2)
