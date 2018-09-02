import numpy as np
import triDobjects as tD


class Particle(object):
    """
    Parent class for particles.
    """

    X = U = 0
    Y = V = 1
    Z = W = 2

    def __init__(self, inertia=1.0, gravity=1.0, friction=0.05, size=0.03,
                 colour=np.array([255, 255, 153, 255]), lifetime=2.0,
                 elasticity=1.0):

        self._inertia = inertia
        self._gravity = gravity
        self._friction = friction
        self._size = size
        self._colour = colour
        self._lifetime = lifetime
        self._elasticity = elasticity
        self._model = tD.TriD(scale=size)

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
        return self._friction

    @friction.setter
    def friction(self, val):
        self._friction = val

    @property
    def patches(self):
        self._model.yaw = np.random.random() * 2 * np.pi
        self._model.pitch = np.random.random() * 2 * np.pi
        self._model.roll = np.random.random() * 2 * np.pi
        return self._model.patches

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

    @property
    def elasticity(self):
        return self._elasticity

    @elasticity.setter
    def elasticity(self, val):
        self._elasticity = val


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
        self._colours = np.empty((0, 4))
        self._visible = True

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
    def visible(self):
        return self._visible

    @visible.setter
    def visible(self, val):
        self._visible = val

    @property
    def positions(self):
        return self._positions

    @positions.setter
    def positions(self, val):
        self._positions = val

    @property
    def patch_positions(self):
        return (self.positions[:, np.newaxis, np.newaxis, :] +
                self.particle.patches[np.newaxis, :, :, :]).mean(-2).reshape(
                    self.number * 4, 3)

    @property
    def patches(self):
        return (self.positions[:, np.newaxis, np.newaxis, :] +
                self.particle.patches[np.newaxis, :, :, :]).reshape(
                    self.number * 4, 3, 3)

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

    @property
    def ages(self):
        return self._ages

    @ages.setter
    def ages(self, val):
        self._ages = val

    @property
    def colours(self):
        return self._colours

    @colours.setter
    def colours(self, val):
        self._colours = val

    @property
    def patch_colours(self):
        return (self._colours * np.ones((4, 1, 1))).reshape(self.number * 4, 4)

    def move(self, dt=0.03125):
        self.apply_forces()
        self.velocities += self.accelerations * dt
        self.positions += self.velocities * dt
        self.ages += dt

    def apply_forces(self):
        forces = (-self.particle.friction * self.velocities +
                  self.particle.gravity * self.particle.inertia)
        self.accelerations = forces / self.particle.inertia

    def bounce(self, world, n):
        normals = world.normals[int(self.positions[n, self.X]),
                                int(self.positions[n, self.Y])]
        self.velocities[n] -= ((1 + self.particle.elasticity) * normals *
                               (self.velocities[n] *
                                normals).sum(-1)[..., np.newaxis])

    def impose_boundary_conditions(self, world):
        self.cull_aged()

        self.positions[:, self.X] %= world.shape[self.X]
        self.positions[:, self.Y] %= world.shape[self.Y]

        heights = world.map_positions[
            self.positions[:, self.X].astype(np.int),
            self.positions[:, self.Y].astype(np.int), self.Z]

        heights = np.where(heights < 0, 0, heights)

        bouncers = np.where(self.positions[:, self.Z] < heights)[0]
        for n in bouncers:
            self.positions[n, self.Z] = heights[n]
            self.bounce(world, n)

    def add_particle(self, position, velocity, acceleration, age=0.0,
                     colour=None):
        self.positions = np.r_[self.positions, position[np.newaxis]]
        self.velocities = np.r_[self.velocities, velocity[np.newaxis]]
        self.accelerations = np.r_[self.accelerations,
                                   acceleration[np.newaxis]]
        self.ages = np.r_[self.ages, age]
        if colour is None:
            self.colours = np.r_[self.colours,
                                 self.particle.colour[np.newaxis]]
        else:
            self.colours = np.r_[self.colours, colour[np.newaxis]]

    def delete_particle(self, n):
        indices = np.r_[np.arange(n), np.arange(self.positions.shape[0])]
        self.positions = self.positions[indices]
        self.velocities = self.velocities[indices]
        self.accelerations = self.accelerations[indices]
        self.ages = self.ages[indices]
        self.colours = self.colours[indices]

    def delete_particles(self, to_delete):
        indices = np.setdiff1d(np.arange(self.number), to_delete)
        self.positions = self.positions[indices]
        self.velocities = self.velocities[indices]
        self.accelerations = self.accelerations[indices]
        self.ages = self.ages[indices]
        self.colours = self.colours[indices]

    def cull_aged(self):
        if (self.ages > self.particle.lifetime).any():
            indices = np.where(self.ages > self.particle.lifetime)[0]
            self.delete_particles(indices)


class Shots(Particles):
    def __init__(self, particle=Particle()):
        self._particle = particle
        self._positions = np.empty((0, 3))
        self._velocities = np.empty((0, 3))
        self._accelerations = np.empty((0, 3))
        self._ages = np.empty((0))
        self._colours = np.empty((0, 4))
        self._visible = True

    def impose_boundary_conditions(self, world):
        self.cull_aged()

        if self.number:
            self.positions[:, self.X] %= world.shape[self.X]
            self.positions[:, self.Y] %= world.shape[self.Y]

            heights = world.map_positions[
                self.positions[:, self.X].astype(np.int),
                self.positions[:, self.Y].astype(np.int), self.Z]

            heights = np.where(heights < 0, 0, heights)

            bouncers = np.where(self.positions[:, self.Z] < heights)[0]
            if bouncers.size:
                positions = self.positions[bouncers]

                velocities = self.velocities[bouncers]

                colours = world.colours[
                    self.positions[bouncers, self.X].astype(np.int),
                    self.positions[bouncers, self.Y].astype(np.int)]

                self.delete_particles(bouncers)

                return positions, velocities, colours

    def cull_aged(self):
        if self.ages[0] > self.particle.lifetime:
            self.positions = self.positions[1:]
            self.velocities = self.velocities[1:]
            self.accelerations = self.accelerations[1:]
            self.ages = self.ages[1:]
            self.colours = self.colours[1:]


class Shrapnel(Particles):
    def __init__(self, particle=Particle(friction=0.5, lifetime=0.5,
                                         elasticity=np.sqrt(3) * 0.5)):
        self._particle = particle
        self._positions = np.empty((0, 3))
        self._velocities = np.empty((0, 3))
        self._accelerations = np.empty((0, 3))
        self._ages = np.empty((0))
        self._colours = np.empty((0, 4))
        self._visible = True

    def add_particles(self, positions, velocities, colours):
        N = np.random.randint(4, 10)
        positions = (positions + np.zeros(np.r_[N, positions.shape])).reshape(
            (positions.shape[0] * N, 3))
        velocities = (velocities * (1.0 / np.sqrt(N)) + 2 * (np.random.random(
            np.r_[N, velocities.shape]) - 0.5)).reshape(
                (velocities.shape[0] * N, 3))
        colours = (colours * (0.125 + 0.5 * np.random.random(
            np.r_[N, colours.shape]))).reshape((colours.shape[0] * N, 4))

        self._positions = np.r_[self._positions, positions]
        self._colours = np.r_[self._colours, colours]
        self._velocities = np.r_[self._velocities, velocities]
        self._accelerations = np.r_[self._accelerations,
                                    np.zeros(positions.shape)]
        self._ages = np.r_[self._ages, np.random.random(positions.shape[0]) *
                           self.particle.lifetime]

    def move(self, dt=0.03125):
        self.apply_forces()
        self.velocities += self.accelerations * dt
        self.positions += self.velocities * dt
        self.ages += dt
        self.colours *= np.array([1.3, 1.3, 1.3, 1.0])


class Exhaust(Particles):
    def __init__(self, particle=Particle(
            friction=0.125, lifetime=1.618, elasticity=0.25,
            colour=np.array([255, 255, 153, 255]))):
        self._particle = particle
        self._positions = np.empty((0, 3))
        self._velocities = np.empty((0, 3))
        self._accelerations = np.empty((0, 3))
        self._ages = np.empty((0))
        self._colours = np.empty((0, 4))
        self._visible = True

    def impose_boundary_conditions(self, world):
        self.cull_aged()

        if self.number:
            self.positions[:, self.X] %= world.shape[self.X]
            self.positions[:, self.Y] %= world.shape[self.Y]

            heights = world.map_positions[
                self.positions[:, self.X].astype(np.int),
                self.positions[:, self.Y].astype(np.int), self.Z]

            heights = np.where(heights < 0, 0, heights)

            bouncers = np.where(self.positions[:, self.Z] < heights)[0]
            if bouncers.size:
                positions = self.positions[bouncers]

                velocities = self.velocities[bouncers]

                colours = world.colours[
                    self.positions[bouncers, self.X].astype(np.int),
                    self.positions[bouncers, self.Y].astype(np.int)]

                self.delete_particles(bouncers)

                return positions, velocities, colours

    def add_particle(self, position, velocity, acceleration, age=0.0,
                     colour=None):
        self.positions = np.r_[self.positions, position[np.newaxis]]
        self.velocities = np.r_[self.velocities, velocity[np.newaxis]]
        self.accelerations = np.r_[self.accelerations,
                                   acceleration[np.newaxis]]
        self.ages = np.r_[self.ages, age + np.random.random() *
                          self.particle.lifetime]

        if colour is None:
            self.colours = np.r_[self.colours,
                                 (0.5 + np.random.random((1, 4))) *
                                 self.particle.colour[np.newaxis]]
        else:
            self.colours = np.r_[self.colours, colour[np.newaxis]]

    def add_particles(self, positions, velocities, accelerations,
                      colours=None):
        N = positions.shape[0]
        self.positions = np.r_[self.positions, positions]
        self.velocities = np.r_[self.velocities, velocities]
        self.accelerations = np.r_[self.accelerations, accelerations]
        self.ages = np.r_[self.ages, np.random.random(N) *
                          self.particle.lifetime]

        if colours is None:
            self.colours = np.r_[self.colours,
                                 (0.5 + np.random.random((N, 4))) *
                                 self.particle.colour[np.newaxis]]
        else:
            self.colours = np.r_[self.colours, colours]

    def move(self, dt=0.03125):
        self.apply_forces()
        self.velocities += self.accelerations * dt
        self.positions += self.velocities * dt
        self.ages += dt
        self.colours *= np.array([0.96, 0.92, 0.88, 1.0])


class Stars(Particles):
    """
    TODO:
        * Change  world --> view.
        * map coordinates to ((0, 0); (view.max())
        * make a return, which offsets by player X and Y.
    """

    def __init__(self, N, view, mean_speed=1.0, min_height=21.0,
                 max_height=42.0, particle=Particle(
            gravity=0.0, friction=0.0, lifetime=1.618, elasticity=0.0,
            colour=np.array([204, 102, 204, 255]))):
        self._particle = particle
        self._positions = np.empty((0, 3))
        self._velocities = np.empty((0, 3))
        self._accelerations = np.empty((0, 3))
        self._ages = np.empty((0))
        self._colours = np.empty((0, 4))
        self._min_height = min_height
        self._max_height = max_height
        self._view = view
        self._offset = np.zeros(3)
        self.add_particles(N, mean_speed)
        self._visible = True

    @property
    def min_height(self):
        return self._min_height

    @min_height.setter
    def min_height(self, val):
        self._min_height = val

    @property
    def max_height(self):
        return self._max_height

    @max_height.setter
    def max_height(self, val):
        self._max_height = val

    def add_particles(self, N, mean_speed=1.0, colour=None):
        x = np.random.random(N) * self._view[self.X]
        y = np.random.random(N) * self._view[self.Y]
        z = (np.random.random(N) * (self._max_height - self._min_height) +
             self._min_height)

        positions = np.c_[x, y, z]

        velocities = (2.0 * np.random.random((N, 3)) - 1.0) * mean_speed

        self._positions = np.r_[self._positions, positions]
        self.velocities = np.r_[self.velocities, velocities]
        self.accelerations = np.empty((self.number, 3))
        self.ages = np.empty(self.number)

        if colour is None:
            self.colours = np.r_[self.colours,
                                 (0.5 + np.random.random((N, 4))) *
                                 self.particle.colour[np.newaxis]]
        else:
            self.colours = np.r_[self.colours, colour * np.ones((N, 4))]

    def move(self, velocity, dt=0.03125):
        self._positions += (self.velocities - velocity[np.newaxis]) * dt

    def impose_boundary_conditions(self):
        if self.number:
            self._positions[:, self.X] = (self._positions[:, self.X] %
                                          self._view[self.X])
            self._positions[:, self.Y] = (self._positions[:, self.Y] %
                                          self._view[self.X])
            self._positions[:, self.Z] = ((self._positions[:, self.Z] -
                                           self._min_height) %
                                          (self._max_height - self._min_height)
                                          + self._min_height)

    def impose_boundary_conditions_old(self, world):
        if self.number:
            self._positions[:, self.X] %= world.shape[self.X]
            self._positions[:, self.Y] %= world.shape[self.Y]
            self._positions[:, self.Z] = ((self.positions[:, self.Z] -
                                           self._min_height) %
                                          (self._max_height - self._min_height)
                                          + self._min_height)

    @property
    def offset(self):
        return self._offset

    @offset.setter
    def offset(self, position):
        self._offset = np.array([position[self.X] - self._view[self.X] * 0.5,
                                 position[self.Y] - self._view[self.Y] * 0.5,
                                 0.0])

    @property
    def positions(self):
        return self._positions + self.offset
