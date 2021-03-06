import numpy as np


class Movable(object):
    """
    Parent class for movable objects.
    """

    X = U = 0
    Y = V = 1
    Z = W = 2

    def __init__(self, model, inertia=1.0, gravity=1.0, friction=1.0,
                 position=np.array([0.0, 0.0, 0.0]),
                 velocity=np.array([0.0, 0.0, 0.0]),
                 acceleration=np.array([0.0, 0.0, 0.0]),
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
        self.apply_forces()
        self.velocity += self.acceleration * dt
        self.position += self.velocity * dt

    def apply_forces(self):
        force = self.friction + self.gravity * self.inertia
        self.acceleration = force / self.inertia

    def bounce(self, world):
        normal = world.normals[int(self.position[self.X]),
                               int(self.position[self.Y])]
        self._velocity -= 2.0 * np.dot(self._velocity, normal) * normal

    def impose_boundary_conditions(self, world):
        self.position[self.X] %= world.shape[self.X]
        self.position[self.Y] %= world.shape[self.Y]

        height = max(0, world.patches[int(self.position[self.X]),
                                      int(self.position[self.Y]),
                                      :, self.Z].max())

        if self.model.bounding_box[0, self.Z] < height:
            self.position[self.Z] += (height -
                                      self.model.bounding_box[0, self.Z])
            self.bounce(world)
            if abs(self.velocity[self.Z]) > 2.5:
                self.model.exploding = True
        elif self.position[self.Z] > 36.0 and self.velocity[self.Z] > 0:
            self.velocity[self.Z] *= 0.9
            if self.acceleration[self.Z] > 0:
                self.acceleration[self.Z] = 0.0


class Player(Movable):
    """
    Player object has health, fuel etc.
    """

    def __init__(self, model, inertia=1.0, gravity=5.0, friction=0.5,
                 position=np.array([0.0, 0.0, 0.0]),
                 velocity=np.array([0.0, 0.0, 0.0]),
                 acceleration=np.array([0.0, 0.0, 0.0]),
                 yaw=0.0, pitch=0.0, roll=0.0,
                 fuel=255, rockets=3, health=255, bombs=3, cool_down=0.0625):

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

        self._fuel = fuel
        self._rockets = rockets
        self._health = health
        self._bombs = bombs
        self._cool_down = cool_down

        self._thrust = False
        self._fire = False
        self._rocket = False
        self._bomb = False

    @property
    def fuel(self):
        return self._fuel

    @fuel.setter
    def fuel(self, val):

        if val > 255:

            val = 255

        elif val < 0:

            val = 0

        self._fuel = val

    @property
    def health(self):
        return self._health

    @health.setter
    def health(self, val):

        if val > 255:

            val = 255

        elif val < 0:

            val = 0

        self._health = val

    @property
    def rockets(self):
        return self._rockets

    @rockets.setter
    def rockets(self, val):

        if val > 3:

            val = 3

        elif val < 0:

            val = 0

        self._rockets = val

    @property
    def bombs(self):
        return self._bombs

    @bombs.setter
    def bombs(self, val):

        if val > 3:

            val = 3

        elif val < 0:

            val = 0

        self._bombs = val

    @property
    def thrust(self):
        return self._thrust

    @thrust.setter
    def thrust(self, val):
        self._thrust = val and True

    @property
    def rocket(self):
        return self._rocket

    @rocket.setter
    def rocket(self, val):
        self._rocket = val and True

    @property
    def fire(self):
        return self._fire

    @fire.setter
    def fire(self, val):
        self._fire = val and True

    @property
    def bomb(self):
        return self._bomb

    @bomb.setter
    def bomb(self, val):
        self._bomb = val and True

    @property
    def cool_down(self):
        return self._cool_down

    @cool_down.setter
    def cool_down(self, val):
        self._cool_down = val

    def apply_forces(self):
        force = (self.friction + self.gravity * self.inertia +
                 20 * (
                     self.thrust
                     and self.position[self.Z] < 36.0
                     and not self.model.exploding
                 ) *
                 self.model.orientation[self.W])

        self.acceleration = force / self.inertia

        if self.model.exploding:
            self.model.explode()
