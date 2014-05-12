import numpy as np


class Movable(object):
    """
    Parent class for movable objects.
    """

    X = U = 0
    Y = V = 1
    Z = W = 2

    def __init__(self, inertia=1.0, gravity=1.0, friction=1.0,
                 position=np.array([0, 0, 0]),
                 velocity=np.array([0, 0, 0]),
                 acceleration=np.array([0, 0, 0])):

        self._inertia = inertia
        self._gravity = gravity
        self._friction = friction
        self._position = position
        self._velocity = velocity
        self._acceleration = acceleration

    @property
    def position(self):
        return self._position

    @position.setter
    def position(self, val):
        self._position = val

    @property
    def velocity(self):
        return self._velocity

    @velocity.setter
    def velocity(self, val):
        self._velocity = val

    @property
    def acceleration(self):
        return self._acceleration

    @acceleration.setter
    def acceleration(self, val):
        self._acceleration = val

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

    def move(self, dt):
        self.position += self.velocity * dt
        self.velocity += self.acceleration * dt

    def apply_force(self, force):
        self.acceleration += force / self.inertia

    def bounce(self):
        self._velocity[self.Z] *= -1
