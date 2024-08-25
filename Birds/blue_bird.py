import math
import pymunk

from game_logic import ImpulseVector, Point2D, get_impulse_vector
from game_object import Bird


class BlueBird(Bird):
    def __init__(
        self,
        image_path: str,
        scale: float,
        impulse_vector: ImpulseVector,
        x: float,
        y: float,
        space: pymunk.Space,
        mass: float = 5,
        radius: float = 12,
        max_impulse: float = 100,
        power_multiplier: float = 50,
        elasticity: float = 0.8,
        friction: float = 1,
        collision_layer: int = 0,
    ):
        super().__init__(
            image_path,
            scale,
            impulse_vector,
            x,
            y,
            space,
            mass,
            radius,
            max_impulse,
            power_multiplier,
            elasticity,
            friction,
            collision_layer,
        )
        self.is_divided = False

    def update(self):
        super().update()
        if self.is_divided:
            self.divide(self.space, self.sprites, self.birds)
            self.is_divided = False  

    def divide(self, space, sprites, birds):
        angles = [-30, 30]
        for angle in angles:
            divided_bird = BlueBird(
                self.image,
                self.scale,
                ImpulseVector(
                    self.shape.body.velocity.length,
                    math.radians(angle) + self.shape.body.angle,
                ),
                self.shape.body.position.x,
                self.shape.body.position.y,
                space,
            )
            divided_bird.shape.body.velocity = self.shape.body.velocity.rotated(
                math.radians(angle)
            )
            sprites.append(divided_bird)
            birds.append(divided_bird)
            if divided_bird.shape.body not in space._bodies:
                space.add(divided_bird.shape, divided_bird.shape.body)

    def power_up(self, space, sprites, birds):
        if not self.is_divided:
            self.space = space
            self.sprites = sprites
            self.birds = birds
            self.is_divided = True
            self.update()
