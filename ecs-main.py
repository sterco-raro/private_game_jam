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

	def __post_init__(self):
		self.image = load_image(self.file_name)
		self.rect = self.image.get_rect()
		self.rect.center = self.starting_position


# -------------------------------------------------------------------------------------------------


class MovementSystem(esper.Processor):
	def __init__(self, min_x, max_x, min_y, max_y):
		super().__init__()
		self.min_x = min_x
		self.max_x = max_x
		self.min_y = min_y
		self.max_y = max_y

	def process(self, dt):
		for ent, (vel, rend) in self.world.get_components(Velocity, Renderable):
			# normalize direction
			if vel.direction.length() > 0:
				vel.direction.normalize_ip()

			# new position
			rend.rect.center += vel.direction * dt * vel.speed/vel.damping_factor

			# clamp
			rend.rect.x = max(self.min_x, rend.rect.x)
			rend.rect.y = max(self.min_y, rend.rect.y)
			rend.rect.x = min(self.max_x - rend.rect.w, rend.rect.x)
			rend.rect.y = min(self.max_y - rend.rect.h, rend.rect.y)


class RenderSystem(esper.Processor):
	def __init__(self, canvas, background):
		super().__init__()
		self.canvas = canvas
		self.background = background

	def process(self, dt):
		# clear
		self.canvas.blit(self.background, (0, 0))
		# render all to canvas
		for ent, rend in self.world.get_component(Renderable):
			self.canvas.blit(rend.image, rend.rect)
		# update display
		pygame.display.update()


class CollisionSystem(esper.Processor):
	def __init__(self):
		pass

	def process(self, dt):
		# do stuff
		pass


# -------------------------------------------------------------------------------------------------


def run():
	pygame.init()
	pygame.mouse.set_visible(False)
	viewport = pygame.display.set_mode(SCREEN_SIZE.size)
	pygame.display.set_caption("ECS CONVERSION")

	clock = pygame.time.Clock()

	world = pygame.Surface((WORLD_WIDTH, WORLD_HEIGHT)).convert()
	canvas = pygame.Surface((WORLD_WIDTH, WORLD_HEIGHT)).convert()

	tilemap = Tilemap(size=(MAP_WIDTH, MAP_HEIGHT), file_name=LEVEL_ARENA)
	tilemap.render(world, False)

	ecsworld = esper.World()
	player = ecsworld.create_entity()
	ecsworld.add_component(player, Velocity())
	ecsworld.add_component(player, Renderable(starting_position=pygame.Vector2(WORLD_WIDTH/2, WORLD_HEIGHT/2)))

	ecsworld.add_processor(RenderSystem(canvas=canvas, background=world))
	ecsworld.add_processor(MovementSystem(min_x=0, max_x=WORLD_WIDTH, min_y=0, max_y=WORLD_HEIGHT))

	dt = clock.tick(60)
	while 1:
		events = pygame.event.get()
		for event in events:
			if event.type == QUIT:
				return

			if event.type == KEYDOWN:
				if event.key == K_w:
					ecsworld.component_for_entity(player, Velocity).direction[1] += -1
				if event.key == K_s:
					ecsworld.component_for_entity(player, Velocity).direction[1] += 1
				if event.key == K_a:
					ecsworld.component_for_entity(player, Velocity).direction[0] += -1
				if event.key == K_d:
					ecsworld.component_for_entity(player, Velocity).direction[0] += 1
			if event.type == KEYUP:
				if event.key in (K_w, K_s):
					ecsworld.component_for_entity(player, Velocity).direction[1] = 0
				if event.key in (K_a, K_d):
					ecsworld.component_for_entity(player, Velocity).direction[0] = 0

		ecsworld.process(dt)

		viewport.blit(canvas, (0, 0))

		dt = clock.tick(60)


# -------------------------------------------------------------------------------------------------


if __name__ == '__main__':
	run()
	pygame.quit()
