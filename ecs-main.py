#
# Private Game Jam
# Theme: Salto nel vuoto
#
# Authors:
#	unarmedpile@gmail.com
#	serviceoftaxi@gmail.com
#


# TODO BUG movement is slower when direction is positive


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


@dataclass()
class BasicSprite:
	file_name: str = "fatso.png"
	starting_position: tuple = (0, 0)
	flippable: bool = False
	flipped: bool = False
	is_moving_left: bool = False

	def __post_init__(self):
		self.image = load_image(self.file_name)
		if self.flipped:
			self.image = pygame.transform.flip(self.image, False, True)
		self.rect = self.image.get_rect()
		self.rect.center = self.starting_position


@dataclass
class PlayerController:
	active: bool = True


@dataclass
class SimpleCamera:
	width: int
	height: int
	target: BasicSprite

	def __post_init__(self):
		self.rect = pygame.Rect(0, 0, self.width, self.height)


@dataclass
class Equippable:
	parent: int
	original_image: pygame.Surface
	offset_x: int = 0
	offset_y: int = 0


@dataclass
class Target:
	current: int = -1


# -------------------------------------------------------------------------------------------------


class RenderSystem(esper.Processor):
	def __init__(self, canvas, background, screen, camera):
		super().__init__()
		self.canvas = canvas
		self.background = background
		self.screen = screen
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
		for ent, sprite in self.world.get_component(BasicSprite):
			if sprite.flippable:
				self.flip_sprite(sprite)
			self.canvas.blit(sprite.image, sprite.rect)
		# render to screen
		self.screen.blit(self.canvas, (0, 0), self.camera.rect)
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
		for ent, (vel, sprite) in self.world.get_components(Velocity, BasicSprite):
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


class CrosshairSystem(esper.Processor):

	def __init__(self, crosshair, camera_target):
		super().__init__()
		self.crosshair = crosshair
		self.camera_target = camera_target

	def process(self, dt):
		# do nothing when cursor is absent
		if not self.crosshair: return
		# get cursor and camera
		cursor = self.world.component_for_entity(self.crosshair, BasicSprite)
		camera = self.world.component_for_entity(self.camera_target, SimpleCamera)
		# get mouse position
		position = pygame.mouse.get_pos()
		# update cursor position based on camera viewport
		cursor.rect.center = pygame.Vector2(position[0] + camera.rect.x, position[1] + camera.rect.y)


class WeaponSystem(esper.Processor):

	def __init__(self):
		super().__init__()

	def process(self, dt):
		for ent, (sprite, equip, target) in self.world.get_components(BasicSprite, Equippable, Target):
			# Get parent entity sprite
			parent_sprite = self.world.component_for_entity(equip.parent, BasicSprite)
			# Default stance
			if target.current == -1:
				lookdir = pygame.Vector2(-1, 0)
			# Get vector pointing at current target
			else:
				target_sprite = self.world.component_for_entity(target.current, BasicSprite)
				lookdir = pygame.Vector2(target_sprite.rect.x - parent_sprite.rect.x, target_sprite.rect.y - parent_sprite.rect.y)
				lookdir = lookdir.rotate(90)
				lookdir.normalize_ip()
			# Get current rotation angle based on lookdir
			rotation_angle = lookdir.angle_to((0, 1))
			# Apply Equippable offset
			sprite.rect.center = (	parent_sprite.rect.center[0] + equip.offset_x,
									parent_sprite.rect.center[1] + equip.offset_y)
			# Rotate sprite
			sprite.image = pygame.transform.rotate(equip.original_image, rotation_angle)


class ViewportSystem(esper.Processor):

	def __init__(self, max_width, max_height):
		super().__init__()
		self.max_width = max_width
		self.max_height = max_height

	def process(self, dt):
		for ent, (cam, sprite) in self.world.get_components(SimpleCamera, BasicSprite):
			# center
			x = cam.target.rect.centerx - cam.width // 2
			y = cam.target.rect.centery - cam.height // 2
			# clamp
			x = min(self.max_width - cam.width, max(0, x))
			y = min(self.max_height - cam.height, max(0, y))
			# update position
			cam.rect.x = x
			cam.rect.y = y


# -------------------------------------------------------------------------------------------------


def create_level_arena():
	"""TODO docstring for create_level_arena"""
	# Screen viewport
	viewport = pygame.display.set_mode(SCREEN_SIZE.size)
	# Window title
	pygame.display.set_caption("POSTE ITALIANE")
	# Drawing surfaces
	canvas = pygame.Surface((WORLD_WIDTH, WORLD_HEIGHT)).convert()
	background = pygame.Surface((WORLD_WIDTH, WORLD_HEIGHT)).convert()
	# Background map
	tilemap = Tilemap(size=(MAP_WIDTH, MAP_HEIGHT), file_name=LEVEL_ARENA)
	tilemap.render(background, False)
	# ECS container object
	world = esper.World()
	# Mouse cursor entity
	crosshair = world.create_entity()
	world.add_component(crosshair, BasicSprite(file_name="cursor_crosshair.png"))
	# Player entity
	player = world.create_entity()
	player_x = WORLD_WIDTH//2 - TILE_SIZE//2
	player_y = WORLD_HEIGHT//2 - TILE_SIZE//2
	player_sprite = BasicSprite(starting_position=pygame.Vector2(player_x, player_y), flippable=True)
	camera = SimpleCamera(width=VIEWPORT_WIDTH, height=VIEWPORT_HEIGHT, target=player_sprite)
	world.add_component(player, Velocity())
	world.add_component(player, player_sprite)
	world.add_component(player, PlayerController())
	world.add_component(player, camera)
	world.add_component(player, Target(current=crosshair))
	# Player weapons
	weapon_left = world.create_entity()
	weapon_left_sprite = BasicSprite(starting_position=pygame.Vector2(player_x - 20, player_y), file_name="weap_hand_L.png", flipped=True)
	world.add_component(weapon_left, Velocity())
	world.add_component(weapon_left, weapon_left_sprite)
	world.add_component(weapon_left, Equippable(parent=player, original_image=weapon_left_sprite.image, offset_x=-20))
	world.add_component(weapon_left, Target(current=crosshair))
	weapon_right = world.create_entity()
	weapon_right_sprite = BasicSprite(starting_position=pygame.Vector2(player_x + 20, player_y), file_name="weap_hand_L.png")
	world.add_component(weapon_right, Velocity())
	world.add_component(weapon_right, weapon_right_sprite)
	world.add_component(weapon_right, Equippable(parent=player, original_image=weapon_right_sprite.image, offset_x=20))
	world.add_component(weapon_right, Target(current=crosshair))
	# Add systems to world
	world.add_processor(RenderSystem(canvas=canvas, background=background, screen=viewport, camera=camera))
	world.add_processor(InputSystem())
	world.add_processor(MovementSystem(min_x=0, max_x=WORLD_WIDTH, min_y=0, max_y=WORLD_HEIGHT))
	world.add_processor(CrosshairSystem(crosshair=crosshair, camera_target=player))
	world.add_processor(WeaponSystem())
	world.add_processor(ViewportSystem(max_width=WORLD_WIDTH, max_height=WORLD_HEIGHT))
	# Return level instance (ECS world)
	return world


# -------------------------------------------------------------------------------------------------


def run():
	# Initialize pygame
	pygame.init()
	pygame.mouse.set_visible(False)
	# Create a clock instance (FPS limit)
	clock = pygame.time.Clock()
	# Time passed since last tick
	dt = 0

	# Generate level and get related world instance
	world = create_level_arena()

	events = None
	while 1:
		# General events handler
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
