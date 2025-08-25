import json
import math
import logging
import arcade
import pymunk

from Birds.blue_bird import BlueBird
from Birds.yellow_bird import YellowBird
from game_object import Bird, Column, Pig
from game_logic import get_impulse_vector, Point2D, get_distance
from levels import levels, LevelData

logging.basicConfig(level=logging.DEBUG)
logging.getLogger("arcade").setLevel(logging.WARNING)
logging.getLogger("pymunk").setLevel(logging.WARNING)
logging.getLogger("PIL").setLevel(logging.WARNING)

logger = logging.getLogger("main")

WIDTH = 1800
HEIGHT = 800
TITLE = "Angry birds"
GRAVITY = -900


class App(arcade.Window):
    def __init__(self):
        super().__init__(WIDTH, HEIGHT, TITLE)
        # Create a sprite list for the background
        self.background_list = arcade.SpriteList()
        # Load the background texture
        background_texture = arcade.load_texture("assets/img/background3.png")
        
        # Calculate scale to fit screen
        scale_width = WIDTH / background_texture.width
        scale_height = HEIGHT / background_texture.height
        scale = max(scale_width, scale_height)
        
        # Create a background sprite
        background_sprite = arcade.Sprite(
            "assets/img/background3.png",
            scale=scale,
            center_x=WIDTH // 2,
            center_y=HEIGHT // 2
        )
        self.background_list.append(background_sprite)
        
        # Slingshot parameters
        self.slingshot_x = 300
        self.slingshot_y = 80
        self.slingshot_width = 40
        self.max_pull_distance = 120

        # Create Pymunk space
        self.space = pymunk.Space()
        self.space.gravity = (0, GRAVITY)

        # Add floor
        floor_body = pymunk.Body(body_type=pymunk.Body.STATIC)
        floor_shape = pymunk.Segment(floor_body, [0, 15], [WIDTH, 15], 0.0)
        floor_shape.friction = 10
        self.space.add(floor_body, floor_shape)

        # Birds
        self.bird_types = [Bird, BlueBird, YellowBird]
        self.current_bird_index = 0
        self.current_bird_type = self.bird_types[self.current_bird_index]

        # Sprites
        self.sprites = arcade.SpriteList()
        self.birds = arcade.SpriteList()
        self.world = arcade.SpriteList()
        self.current_level = 0
        self.load_level(self.current_level)

        # Drag line
        self.start_point = Point2D()
        self.end_point = Point2D()
        self.draw_line = False

        # Collision handler
        self.handler = self.space.add_default_collision_handler()
        self.handler.post_solve = self.collision_handler

    def load_level(self, level_index: int):
        self.clear_level()
        level_data = levels[level_index]
        self.add_columns(level_data)
        self.add_pigs(level_data)

    def clear_level(self):
        for sprite in self.world:
            self.space.remove(sprite.shape, sprite.body)
        self.world.clear()
        self.birds.clear()
        self.sprites.clear()

    def collision_handler(self, arbiter, space, data):
        impulse_norm = arbiter.total_impulse.length
        if impulse_norm < 100:
            return True
        logger.debug(impulse_norm)
        if impulse_norm > 1200:
            for obj in self.world:
                if obj.shape in arbiter.shapes:
                    obj.remove_from_sprite_lists()
                    self.space.remove(obj.shape, obj.body)
        return True

    def add_columns(self, level_data: LevelData):
        for column in level_data.columns:
            if len(column) == 3:
                x, y, horizontal = column
            else:
                x, y = column
                horizontal = False
            column = Column(x, y, self.space, horizontal)
            self.sprites.append(column)
            self.world.append(column)

    def add_pigs(self, level_data: LevelData):
        for x, y in level_data.pigs:
            pig = Pig(x, y, self.space)
            self.sprites.append(pig)
            self.world.append(pig)

    def on_update(self, delta_time: float):
        self.space.step(1 / 60.0)
        self.update_collisions()
        for bird in self.birds:
            if bird.timer > 4:
                bird.remove_from_sprite_lists()
                self.space.remove(bird.shape, bird.body)
        self.sprites.update()
        self.check_level_complete()

    def update_collisions(self):
        pass

    def on_mouse_press(self, x, y, button, modifiers):
        if button == arcade.MOUSE_BUTTON_LEFT:
            distance_to_slingshot = ((x - self.slingshot_x) ** 2 + (y - self.slingshot_y) ** 2) ** 0.5
            if distance_to_slingshot < 50:
                self.start_point = Point2D(self.slingshot_x, self.slingshot_y)
                self.end_point = Point2D(x, y)
                self.draw_line = True
                logger.debug(f"Start Point: {self.start_point}")

    def on_mouse_drag(self, x: int, y: int, dx: int, dy: int, buttons: int, modifiers: int):
        if buttons == arcade.MOUSE_BUTTON_LEFT and self.draw_line:
            dx = x - self.slingshot_x
            dy = y - self.slingshot_y
            distance = (dx * dx + dy * dy) ** 0.5
            if distance > self.max_pull_distance:
                factor = self.max_pull_distance / distance
                x = self.slingshot_x + dx * factor
                y = self.slingshot_y + dy * factor
            self.end_point = Point2D(x, y)
            logger.debug(f"Dragging to: {self.end_point}")

    def on_mouse_release(self, x: int, y: int, button: int, modifiers: int):
        if button == arcade.MOUSE_BUTTON_LEFT and self.draw_line:
            logger.debug(f"Releasing from: {self.end_point}")
            self.draw_line = False
            impulse_vector = get_impulse_vector(self.start_point, self.end_point)
            self.switch_bird()
            if self.current_bird_type == Bird:
                bird = Bird("assets/img/red-bird3.png", 1, impulse_vector, x, y, self.space)
            elif self.current_bird_type == BlueBird:
                bird = BlueBird("assets/img/blue.png", 0.2, impulse_vector, x, y, self.space)
            elif self.current_bird_type == YellowBird:
                bird = YellowBird("assets/img/yellowBird.png", 0.05, impulse_vector, x, y, self.space)
            self.sprites.append(bird)
            self.current_bird = bird
            self.birds.append(bird)

    def on_key_press(self, key, modifiers):
        if key == arcade.key.SPACE and hasattr(self, 'current_bird'):
            if self.current_bird_type == BlueBird:
                self.current_bird.power_up(self.space, self.sprites, self.birds)
            elif self.current_bird_type == YellowBird:
                self.current_bird.power_up()
        elif key == arcade.key.LEFT:
            self.current_level += 1
            if self.current_level >= len(levels):
                self.current_level = 0
            self.load_level(self.current_level)

    def switch_bird(self):
        self.current_bird_index = (self.current_bird_index + 1) % 3
        self.current_bird_type = self.bird_types[self.current_bird_index]

    def on_draw(self):
        self.clear()
        self.background_list.draw()
        # Slingshot base
        arcade.draw_lrbt_rectangle_filled(
            self.slingshot_x - 10,
            self.slingshot_x + 10,
            self.slingshot_y - 100,
            self.slingshot_y,
            arcade.color.BROWN
        )
        left_arm_x = self.slingshot_x - self.slingshot_width
        right_arm_x = self.slingshot_x + self.slingshot_width
        arm_y = self.slingshot_y + 40
        arcade.draw_line(self.slingshot_x, self.slingshot_y, left_arm_x, arm_y, arcade.color.BROWN, 5)
        arcade.draw_line(self.slingshot_x, self.slingshot_y, right_arm_x, arm_y, arcade.color.BROWN, 5)
        if self.draw_line:
            arcade.draw_line(left_arm_x, arm_y, self.end_point.x, self.end_point.y, arcade.color.BLACK, 3)
            arcade.draw_line(right_arm_x, arm_y, self.end_point.x, self.end_point.y, arcade.color.BLACK, 3)
        self.sprites.draw()

    def check_level_complete(self):
        if not self.world.sprite_list:
            self.current_level += 1
            if self.current_level < len(levels):
                self.load_level(self.current_level)
            else:
                print("¡Volviendo al nivel 1!")
                self.current_level = 0
                self.load_level(self.current_level)
                self.current_bird_index = 0
                self.current_bird_type = self.bird_types[self.current_bird_index]


def main():
    app = App()
    arcade.run()


if __name__ == "__main__":
    main()
