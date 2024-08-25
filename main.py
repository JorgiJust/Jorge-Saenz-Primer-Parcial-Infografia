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
        self.background = arcade.load_texture("assets/img/background3.png")
        # crear espacio de pymunk
        self.space = pymunk.Space()
        self.space.gravity = (0, GRAVITY)

        # agregar piso
        floor_body = pymunk.Body(body_type=pymunk.Body.STATIC)
        floor_shape = pymunk.Segment(floor_body, [0, 15], [WIDTH, 15], 0.0)
        floor_shape.friction = 10
        self.space.add(floor_body, floor_shape)
        self.bird_types = [Bird, BlueBird, YellowBird]
        self.current_bird_index = 0
        self.current_bird_type = self.bird_types[self.current_bird_index]

        self.sprites = arcade.SpriteList()
        self.birds = arcade.SpriteList()
        self.world = arcade.SpriteList()
        self.current_level = 0
        self.load_level(self.current_level)

        self.start_point = Point2D()
        self.end_point = Point2D()
        self.distance = 0
        self.draw_line = False

        # agregar un collision handler
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
        self.space.step(1 / 60.0)  # actualiza la simulacion de las fisicas
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
            self.start_point = Point2D(x, y)
            self.end_point = Point2D(x, y)
            self.draw_line = True
            logger.debug(f"Start Point: {self.start_point}")

    def on_mouse_drag(
        self, x: int, y: int, dx: int, dy: int, buttons: int, modifiers: int
    ):
        if buttons == arcade.MOUSE_BUTTON_LEFT:
            self.end_point = Point2D(x, y)
            logger.debug(f"Dragging to: {self.end_point}")

    def on_mouse_release(self, x: int, y: int, button: int, modifiers: int):
        if button == arcade.MOUSE_BUTTON_LEFT:
            logger.debug(f"Releasing from: {self.end_point}")
            self.draw_line = False
            impulse_vector = get_impulse_vector(self.start_point, self.end_point)

            if self.current_bird_type == Bird:
                bird = Bird(
                    "assets/img/red-bird3.png", 1, impulse_vector, x, y, self.space
                )
            elif self.current_bird_type == BlueBird:
                bird = BlueBird(
                    "assets/img/blue.png", 0.2, impulse_vector, x, y, self.space
                )
            elif self.current_bird_type == YellowBird:
                bird = YellowBird(
                    "assets/img/yellowBird.png", 0.05, impulse_vector, x, y, self.space
                )

            self.sprites.append(bird)
            self.current_bird = bird
            self.birds.append(bird)

    def on_key_press(self, key, modifiers):
        if key == arcade.key.TAB:
            self.switch_bird()
        elif key == arcade.key.SPACE:
            print(f"tipo de mi pajaro {type(self.current_bird)}")
            if self.current_bird_type == BlueBird:
                self.current_bird.power_up(self.space, self.sprites, self.birds)
            self.current_bird.power_up()
        elif key == arcade.key.LEFT:
            print("xd")
            self.current_level += 1
            self.load_level(self.current_level)

    def switch_bird(self):
        self.current_bird_index = (self.current_bird_index + 1) % len(self.bird_types)
        self.current_bird_type = self.bird_types[self.current_bird_index]
        print(
            f"Switched to {self.current_bird_type.__name__} with index {self.current_bird_index}"
        )

    def on_draw(self):
        arcade.start_render()
        arcade.draw_lrwh_rectangle_textured(0, 0, WIDTH, HEIGHT, self.background)
        self.sprites.draw()
        if self.draw_line:
            arcade.draw_line(
                self.start_point.x,
                self.start_point.y,
                self.end_point.x,
                self.end_point.y,
                arcade.color.BLACK,
                3,
            )

    def check_level_complete(self):
        if not self.world.sprite_list:
            self.current_level += 1
            if self.current_level < len(levels):
                self.load_level(self.current_level)
            else:
                print("Congratulations! You've completed all levels!")
                arcade.close_window()


def main():
    app = App()
    arcade.run()


if __name__ == "__main__":
    main()
