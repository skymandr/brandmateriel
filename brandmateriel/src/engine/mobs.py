import numpy as np


class Movable(object):
    """
    Parent class for movable objects.
    """

    X = U = 0
    Y = V = 1
    Z = W = 2

    def __init__(self, model, inertia=1.0, gravity=1.0, friction=1.0,
                 position=np.array([0, 0, 0]),
                 velocity=np.array([0, 0, 0]),
                 acceleration=np.array([0, 0, 0]),
                 yaw=0.0, pitch=0.0, roll=0.0):

        self._model = model
        self._inertia = inertia
        self._gravity = gravity
        self._friction = friction
        self._position = position
        self._velocity = velocity
        self._acceleration = acceleration

        self._model.position = position
        self._model.yaw = yaw
        self._model.pitch = pitch
        self._model.roll = roll

    @property
    def model(self):
        return self._model

    @property
    def position(self):
        return self._position

    @position.setter
    def position(self, val):
        self._position = val
        self._model.position = val

    @property
    def yaw(self):
        return self._model.yaw

    @yaw.setter
    def yaw(self, val):
        self._model.yaw = val

    @property
    def pitch(self):
        return self._model.pitch

    @pitch.setter
    def pitch(self, val):
        self._model.pitch = val

    @property
    def roll(self):
        return self._model.roll

    @roll.setter
    def roll(self, val):
        self._model.roll = val

    @property
    def bounding_box(self):
        return self._model.bounding_box

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

    def move(self, dt=0.03125):
        self.position += self.velocity * dt
        self.velocity += self.acceleration * dt

    def apply_force(self, force):
        self.acceleration += force / self.inertia

    def bounce(self):
        self._velocity[self.Z] = np.abs(self._velocity[self.Z])

    def impose_boundary_conditions(self, map):
        self.position[self.X] %= map.shape[self.X]
        self.position[self.Y] %= map.shape[self.Y]
        height = map.positions[self.position[self.X],
                               self.position[self.Y], self.Z]

        if self.position[self.Z] <= height:
            self.position[self.Z] = height
            self.bounce()
