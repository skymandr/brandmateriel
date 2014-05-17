import numpy as np


class Particle(object):
    """
    Parent class for particles.
    """

    X = U = 0
    Y = V = 1
    Z = W = 2

    def __init__(self, inertia=1.0, gravity=1.0, friction=1.0,
                 size=np.array([0.1, 0.1]),
                 colour=np.array([204, 204, 153, 255]),
                 lifetime=1.0):

        self._inertia = inertia
        self._gravity = gravity
        self._friction = friction
        self._size = size
        self._colour = colour
        self._lifetime = lifetime

    @property
    def inertia(self):
        return self._inertia

    @inertia.setter
    def inertia(self, val):
        self._inertia = val

    @property
    def gravity(self):
        return self._gravity * np.array([0, 0, -1])

    @gravity.setter
    def gravity(self, val):
        self._gravity = val

    @property
    def friction(self):
        return -self._friction * self._velocity

    @friction.setter
    def friction(self, val):
        self._friction = val

    @property
    def size(self):
        return self._size

    @size.setter
    def size(self, val):
        self._size = val

    @property
    def patch(self):
        return np.array([
            [self._size[self.X] * 0.5, self._size[self.Y] * 0.5, 0.0],
            [-self._size[self.X] * 0.5, self._size[self.Y] * 0.5, 0.0],
            [-self._size[self.X] * 0.5, -self._size[self.Y] * 0.5, 0.0],
            [self._size[self.X] * 0.5, -self._size[self.Y] * 0.5, 0.0]])

    @property
    def colour(self):
        return self._colour

    @colour.setter
    def colour(self, val):
        self._colour = val

    @property
    def lifetime(self):
        return self._lifetime

    @lifetime.setter
    def lifetime(self, val):
        self._lifetime = val


class Particles(object):

    X = U = 0
    Y = V = 1
    Z = W = 2

    def __init__(self, particle=Particle()):
        self._particle = particle
        self._positions = np.empty((0, 3))
        self._velocities = np.empty((0, 3))
        self._accelerations = np.empty((0, 3))
        self._ages = np.empty((0))

    @property
    def particle(self):
        return self._particle

    @particle.setter
    def particle(self, val):
        self._particle = val

    @property
    def number(self):
        return self.positions.shape[0]

    @property
    def positions(self):
        return self._positions

    @positions.setter
    def positions(self, val):
        self._positions = val

    @property
    def patches(self):
        return (self.positions[:, np.newaxis, :] +
                self.particle.patch[np.newaxis, :])

    @property
    def velocities(self):
        return self._velocities

    @velocities.setter
    def velocities(self, val):
        self._velocities = val

    @property
    def accelerations(self):
        return self._accelerations

    @accelerations.setter
    def accelerations(self, val):
        self._accelerations = val

    def move(self, dt=0.03125):
        self.apply_forces()
        self.velocities += self.accelerations * dt
        self.positions += self.velocities * dt
        self.ages += dt

    @property
    def ages(self):
        return self._ages

    @ages.setter
    def ages(self, val):
        self._ages = val

    def apply_forces(self):
        forces = -(self.particle.friction * self.velocities +
                   np.array([0.0, 0.0, 1.0]) * self.particle.gravity *
                   self.particle.inertia)
        self.acceleration = forces / self.particle.inertia

    def bounce(self, world, n):
        normal = world.normals[self.positions[n, self.X],
                               self.position[n, self.Y]]
        self.velocities[n] -= 2.0 * np.dot(self.velocities[n], normal) * normal

    def impose_boundary_conditions(self, world):
        self.cull_aged()

        self.positions[:, self.X] %= world.shape[self.X]
        self.positions[:, self.Y] %= world.shape[self.Y]

        heights = max(0, world.patches[self.positions[:, self.X],
                                       self.positions[:, self.Y],
                                       :, self.Z].max())

        bouncers = np.where(self.positions[:, self.Z] < heights)
        for n in bouncers:
            self.positions[n, self.Z] = heights[n]
            self.bounce(world, n)

    def add_particle(self, position, velocity, acceleration):
        self.positions = np.r_[self.positions, position[np.newaxis]]
        self.velocities = np.r_[self.velocities, velocity[np.newaxis]]
        self.accelerations = np.r_[self.accelerations,
                                   acceleration[np.newaxis]]
        self.ages = np.r_[self.ages, 0.0]

    def delete_particle(self, n):
        indices = np.r_[np.arange(n), np.arange(self.positions.shape[0])]
        self.positions = self.positions[indices]
        self.velocities = self.velocities[indices]
        self.accelerations = self.accelerations[indices]
        self.ages = self.ages[indices]

    def cull_aged(self):
        if (self.ages > self.particle.lifetime).any():
            indices = np.where(self.ages < self.particle.lifetime)
            self.positions = self.positions[indices]
            self.velocities = self.velocities[indices]
            self.accelerations = self.accelerations[indices]
