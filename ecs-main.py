#
# Private Game Jam
# Theme: Salto nel vuoto
#
# Authors:
#	unarmedpile@gmail.com
#	serviceoftaxi@gmail.com
#


try:
	import sys
	import random
	from dataclasses import dataclass

	import esper
	import pygame
	from pygame.locals import *

	from constants import *
	from utils import load_image
	from game_map import Tilemap

except ImportError as importErr:
	print("Couldn't load module. {}".format(importErr))
	sys.exit(2)


# -------------------------------------------------------------------------------------------------


@dataclass
class Velocity(object):
	speed: int = 32
	direction: pygame.Vector2 = pygame.Vector2(0, 0)
	damping_factor: int = DAMPING_FACTOR


@dataclass
class Renderable:
	file_name: str = "fatso.png"
	starting_position: tuple = (0, 0)
	flippable: bool = True
	flipped: bool = False
	is_moving_left: bool = False

	def __post_init__(self):
		self.image = load_image(self.file_name)
		self.rect = self.image.get_rect()
		self.rect.center = self.starting_position


@dataclass
class PlayerController:
	active: bool = True


@dataclass
class SimpleCamera:
	width: int
	height: int
	target: Renderable

	def __post_init__(self):
		self.rect = pygame.Rect(0, 0, self.width, self.height)


# -------------------------------------------------------------------------------------------------


class RenderSystem(esper.Processor):
	def __init__(self, canvas, background, viewport, camera):
		super().__init__()
		self.canvas = canvas
		self.background = background
		self.viewport = viewport
		self.camera = camera

	def flip_sprite(self, sprite):
		if sprite.is_moving_left and not sprite.flipped:
			sprite.image = pygame.transform.flip(sprite.image, True, False)
			sprite.flipped = True
		elif not sprite.is_moving_left and sprite.flipped:
			sprite.image = pygame.transform.flip(sprite.image, True, False)
			sprite.flipped = False

	def process(self, dt):
		# clear
		self.canvas.blit(self.background, (0, 0))
		# render all to canvas
		for ent, sprite in self.world.get_component(Renderable):
			if sprite.flippable:
				self.flip_sprite(sprite)
			self.canvas.blit(sprite.image, sprite.rect)
		# render to viewport
		self.viewport.blit(self.canvas, (0, 0), self.camera.rect)
		# update display
		pygame.display.update()


class InputSystem(esper.Processor):

	def process(self, dt):
		pressed = pygame.key.get_pressed()
		for ent, (vel, ctrl) in self.world.get_components(Velocity, PlayerController):
			# Skip inactive controllers
			if not ctrl.active: continue
			# Movement direction
			vel.direction = pygame.Vector2(0, 0)
			# Get direction based on keys pressed
			if pressed[pygame.K_w] or pressed[pygame.K_UP]: 	vel.direction += ( 0, -1)
			if pressed[pygame.K_a] or pressed[pygame.K_LEFT]: 	vel.direction += (-1,  0)
			if pressed[pygame.K_s] or pressed[pygame.K_DOWN]: 	vel.direction += ( 0,  1)
			if pressed[pygame.K_d] or pressed[pygame.K_RIGHT]: 	vel.direction += ( 1,  0)


class MovementSystem(esper.Processor):
	def __init__(self, min_x, max_x, min_y, max_y):
		super().__init__()
		self.min_x = min_x
		self.max_x = max_x
		self.min_y = min_y
		self.max_y = max_y

	def process(self, dt):
		for ent, (vel, sprite) in self.world.get_components(Velocity, Renderable):
			# normalize direction
			if vel.direction.length() > 0:
				vel.direction.normalize_ip()

			# new position
			sprite.rect.center += vel.direction * dt * vel.speed/vel.damping_factor

			# clamp
			sprite.rect.x = max(self.min_x, sprite.rect.x)
			sprite.rect.y = max(self.min_y, sprite.rect.y)
			sprite.rect.x = min(self.max_x - sprite.rect.w, sprite.rect.x)
			sprite.rect.y = min(self.max_y - sprite.rect.h, sprite.rect.y)

			# flip sprite when necessary
			sprite.is_moving_left = vel.direction[0] < 0


class ViewportSystem(esper.Processor):

	def __init__(self, max_width, max_height):
		super().__init__()
		self.max_width = max_width
		self.max_height = max_height

	def process(self, dt):
		for ent, (cam, sprite) in self.world.get_components(SimpleCamera, Renderable):
			# center
			x = cam.target.rect.centerx - cam.width // 2
			y = cam.target.rect.centery - cam.height // 2
			# clamp
			x = min(self.max_width - cam.width, max(0, x))
			y = min(self.max_height - cam.height, max(0, y))
			# update position
			cam.rect.x = x
			cam.rect.y = y


class CrosshairSystem(esper.Processor):

	def __init__(self, crosshair, camera_target):
		super().__init__()
		self.crosshair = crosshair
		self.camera_target = camera_target

	def process(self, dt):
		# do nothing when cursor is absent
		if not self.crosshair: return
		# get cursor and camera
		cursor = self.world.component_for_entity(self.crosshair, Renderable)
		camera = self.world.component_for_entity(self.camera_target, SimpleCamera)
		# get mouse position
		position = pygame.mouse.get_pos()
		# update cursor position based on camera viewport
		cursor.rect.center = pygame.Vector2(position[0] + camera.rect.x, position[1] + camera.rect.y)

# -------------------------------------------------------------------------------------------------


def run():
	pygame.init()
	pygame.mouse.set_visible(False)
	viewport = pygame.display.set_mode(SCREEN_SIZE.size)
	pygame.display.set_caption("ECS CONVERSION")

	clock = pygame.time.Clock()

	background = pygame.Surface((WORLD_WIDTH, WORLD_HEIGHT)).convert()
	canvas = pygame.Surface((WORLD_WIDTH, WORLD_HEIGHT)).convert()

	tilemap = Tilemap(size=(MAP_WIDTH, MAP_HEIGHT), file_name=LEVEL_ARENA)
	tilemap.render(background, False)

	world = esper.World()

	player = world.create_entity()
	world.add_component(player, Velocity())
	world.add_component(player, Renderable(starting_position=pygame.Vector2(WORLD_WIDTH/2, WORLD_HEIGHT/2)))
	world.add_component(player, PlayerController())
	world.add_component(player, SimpleCamera(width=VIEWPORT_WIDTH, height=VIEWPORT_HEIGHT, target=world.component_for_entity(player, Renderable)))

	crosshair = world.create_entity()
	world.add_component(crosshair, Renderable(file_name="cursor_crosshair.png", flippable=False))

	world.add_processor(RenderSystem(canvas=canvas, background=background, viewport=viewport, camera=world.component_for_entity(player, SimpleCamera)))
	world.add_processor(InputSystem())
	world.add_processor(MovementSystem(min_x=0, max_x=WORLD_WIDTH, min_y=0, max_y=WORLD_HEIGHT))
	world.add_processor(CrosshairSystem(crosshair=crosshair, camera_target=player))
	world.add_processor(ViewportSystem(max_width=WORLD_WIDTH, max_height=WORLD_HEIGHT))

	dt = 0
	while 1:
		# Handle general events
		events = pygame.event.get()
		for event in events:
			if event.type == QUIT:
				return
		# Update systems
		world.process(dt)
		# Limit fps
		dt = clock.tick(60)


# -------------------------------------------------------------------------------------------------


if __name__ == '__main__':
	run()
	pygame.quit()
