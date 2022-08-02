# Entities

try:
	import sys
	import math
	import pygame

	from utils import load_image
	from constants import MOVEMENT_ANGLE_FIX

except ImportError as importErr:
	print("Couldn't load module. {}".format(importErr))
	sys.exit(2)


# -------------------------------------------------------------------------------------------------


class Player(pygame.sprite.Sprite):
	"""Player entity
	Returns: player object
	Functions: update, move(dx, dy)
	Attributes: step (movement amount), direction_x (x axis direction), direction_y (y axis direction)"""
	def __init__(self, position_xy, step):
		pygame.sprite.Sprite.__init__(self)
		self.image, self.rect = load_image('player.png')
		self.area = pygame.display.get_surface().get_rect()
		self.rect.update(position_xy, (self.rect.width, self.rect.height))
		self.step = step
		self.direction_x = 0
		self.direction_y = 0

	def update(self):
		if self.direction_x != 0 and self.direction_y != 0:
			dx = self.direction_x * (self.step * MOVEMENT_ANGLE_FIX)
			dy = self.direction_y * (self.step * MOVEMENT_ANGLE_FIX)
		else:
			dx = self.direction_x * self.step
			dy = self.direction_y * self.step

		self.rect = self.rect.move((dx, dy))

		pygame.event.pump()

	def change_direction(self, dx, dy):
		self.direction_x += dx
		self.direction_y += dy

	def change_direction_x(self, dx):
		self.direction_x += dx

	def change_direction_y(self, dy):
		self.direction_y += dy
