import math
import pymunk

from game_logic import ImpulseVector, Point2D, get_impulse_vector
from game_object import Bird

# from main import App


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
            self.divide()
            self.is_divided = False  # Reset to prevent continuous division

    def divide(self, space, sprites, birds):
        angles = [-30, 0, 30]
        for angle in angles:
            new_impulse = self.body.velocity.rotated_degrees(angle) * 0.8
            new_impulse_vector = ImpulseVector(new_impulse.angle, new_impulse.length)
            new_bird = BlueBird(
                self.texture.name,
                self.scale * 0.7,
                new_impulse_vector,
                self.body.position.x,
                self.body.position.y,
                space,
                mass=self.shape.mass * 0.5,
                radius=self.shape.radius * 0.7,
            )
            space.add(new_bird.body, new_bird.shape)
            sprites.append(new_bird)
            birds.append(new_bird)
        self.remove_from_sprite_lists()
        space.remove(self.body, self.shape)
