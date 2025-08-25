import math
import arcade
import pymunk
from game_logic import ImpulseVector


class Bird(arcade.Sprite):
    """
    Bird class. This represents an angry bird. All the physics is handled by Pymunk,
    the init method only set some initial properties
    """

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
        elasticity: float = 0.4,
        friction: float = 0.7,
        collision_layer: int = 0,
    ):
        self.image = image_path
        super().__init__(image_path, scale)
        # body
        moment = pymunk.moment_for_circle(mass, 0, radius)
        body = pymunk.Body(mass, moment)
        body.position = (x, y)

        impulse = min(max_impulse, impulse_vector.impulse) * power_multiplier
        impulse_pymunk = impulse * pymunk.Vec2d(1, 0)
        # apply impulse
        body.apply_impulse_at_local_point(impulse_pymunk.rotated(impulse_vector.angle))
        # shape
        shape = pymunk.Circle(body, radius)
        shape.elasticity = elasticity
        shape.friction = friction
        shape.collision_type = collision_layer

        space.add(body, shape)

        self.body = body
        self.shape = shape
        self.timer = 0

    def update(self, delta_time: float = 1 / 60):
        """
        Update the position of the bird sprite based on the physics body position
        """
        self.center_x = self.shape.body.position.x
        self.center_y = self.shape.body.position.y
        self.radians = self.shape.body.angle
        self.timer += delta_time


class Pig(arcade.Sprite):
    def __init__(
        self,
        x: float,
        y: float,
        space: pymunk.Space,
        mass: float = 12,  # Mayor masa para más estabilidad
        elasticity: float = 0.2,  # Menos rebote para reducir daño por caídas
        friction: float = 0.8,  # Más fricción para mejor estabilidad
        collision_layer: int = 0,
    ):
        super().__init__("assets/img/pig_failed.png", 0.1)
        self.mass = mass
        self.space = space
        
        # Crear un cuerpo dinámico desde el inicio
        moment = pymunk.moment_for_circle(mass, 0, self.width / 2 - 3)
        body = pymunk.Body(mass, moment)
        body.position = (x, y)
        body.moment = moment * 0.8  # Aumentar el momento de inercia para más estabilidad
        
        shape = pymunk.Circle(body, self.width / 2 - 3)
        shape.elasticity = elasticity
        shape.friction = friction
        shape.collision_type = collision_layer
        
        self.space.add(body, shape)
        self.body = body
        self.shape = shape
        
    def make_dynamic(self):
        """Convierte el cerdo de estático a dinámico cuando recibe un impacto"""
        if self.body.body_type != pymunk.Body.STATIC:
            return
            
        # Eliminar el cuerpo estático
        self.space.remove(self.shape, self.body)
        
        # Crear nuevo cuerpo dinámico
        moment = pymunk.moment_for_circle(self.mass, 0, self.width / 2 - 3)
        new_body = pymunk.Body(self.mass, moment)
        new_body.position = self.body.position
        
        # Mantener las mismas propiedades de la forma
        new_shape = pymunk.Circle(new_body, self.width / 2 - 3)
        new_shape.elasticity = self.shape.elasticity
        new_shape.friction = self.shape.friction
        new_shape.collision_type = self.shape.collision_type
        
        # Añadir el nuevo cuerpo dinámico
        self.space.add(new_body, new_shape)
        self.body = new_body
        self.shape = new_shape

    def update(self, delta_time: float = 1/60):
        self.center_x = self.shape.body.position.x
        self.center_y = self.shape.body.position.y
        self.radians = self.shape.body.angle


class PassiveObject(arcade.Sprite):
    """
    Passive object that can interact with other objects.
    """

    def __init__(
        self,
        image_path: str,
        x: float,
        y: float,
        space: pymunk.Space,
        mass: float = 8,
        elasticity: float = 0.4,
        friction: float = 0.7,
        collision_layer: int = 0
    ):
        super().__init__(image_path, 1)
        self.space = space
        self.mass = mass

        # Siempre crear cuerpos dinámicos
        moment = pymunk.moment_for_box(mass, (self.width, self.height))
        body = pymunk.Body(mass, moment)
        body.moment = moment * 0.7  # Reduce el momento de inercia para que gire más fácilmente
            
        body.position = (x, y)
        shape = pymunk.Poly.create_box(body, (self.width, self.height))
        shape.elasticity = elasticity
        shape.friction = friction
        shape.collision_type = collision_layer
        self.space.add(body, shape)
        self.body = body
        self.shape = shape

    def make_dynamic(self):
        """Convierte el objeto de estático a dinámico cuando recibe un impacto"""
        if self.body.body_type != pymunk.Body.STATIC:
            return
            
        # Eliminar el cuerpo estático
        self.space.remove(self.shape, self.body)
        
        # Crear nuevo cuerpo dinámico
        moment = pymunk.moment_for_box(self.mass, (self.width, self.height))
        new_body = pymunk.Body(self.mass, moment)
        new_body.position = self.body.position
        new_body.angle = self.body.angle
        new_body.velocity = self.body.velocity
        new_body.angular_velocity = self.body.angular_velocity
        
        # Mantener las mismas propiedades de la forma
        new_shape = pymunk.Poly.create_box(new_body, (self.width, self.height))
        new_shape.elasticity = self.shape.elasticity
        new_shape.friction = self.shape.friction
        new_shape.collision_type = self.shape.collision_type
        
        # Añadir el nuevo cuerpo dinámico
        self.space.add(new_body, new_shape)
        self.body = new_body
        self.shape = new_shape

    def update(self, delta_time: float = 1/60):
        self.center_x = self.shape.body.position.x
        self.center_y = self.shape.body.position.y
        self.radians = self.shape.body.angle

    def power_up(self):
        pass


class Column(PassiveObject):
    def __init__(self, x, y, space, horizontal=False):
        super().__init__(
            "assets/img/column.png", 
            x, 
            y, 
            space,
            mass=15,  # Mayor masa para más estabilidad
            elasticity=0.3,  # Menos rebote
            friction=0.9,  # Más fricción para mejor agarre
        )
        
        if horizontal:
            self.space.remove(self.shape)
            self.body.angle = math.pi / 2
            new_shape = pymunk.Poly.create_box(self.body, (self.height, self.width))
            new_shape.elasticity = 0.3
            new_shape.friction = 0.9
            new_shape.mass = 15
            new_shape.friction = self.shape.friction
            self.space.add(new_shape)
            self.shape = new_shape

    def make_dynamic(self):
        if self.body.body_type != pymunk.Body.STATIC:
            return

        # Eliminar el cuerpo estático
        self.space.remove(self.shape, self.body)
        
        # Crear nuevo cuerpo dinámico
        moment = pymunk.moment_for_box(self.mass, (self.width, self.height))
        new_body = pymunk.Body(self.mass, moment)
        new_body.position = self.body.position
        new_body.angle = self.body.angle
        
        # Crear nueva forma manteniendo las propiedades
        if abs(self.body.angle - math.pi/2) < 0.1:  # Si es horizontal
            new_shape = pymunk.Poly.create_box(new_body, (self.height, self.width))
        else:
            new_shape = pymunk.Poly.create_box(new_body, (self.width, self.height))
        
        new_shape.elasticity = self.shape.elasticity
        new_shape.friction = self.shape.friction
        new_shape.collision_type = self.shape.collision_type
        
        # Añadir el nuevo cuerpo dinámico
        self.space.add(new_body, new_shape)
        self.body = new_body
        self.shape = new_shape
        self.angle = 90

    def update(self, delta_time: float = 1/60):
        super().update()
        self.angle = math.degrees(self.shape.body.angle)


class StaticObject(arcade.Sprite):
    def __init__(
        self,
        image_path: str,
        x: float,
        y: float,
        space: pymunk.Space,
        mass: float = 8,
        elasticity: float = 0.4,
        friction: float = 0.7,
        collision_layer: int = 0,
    ):
        super().__init__(image_path, 1)
