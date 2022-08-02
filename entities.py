# Entities


try:
	import sys
	import pygame

	from utils import load_image

except ImportError as importErr:
	print("Couldn't load module. {}".format(importErr))
	sys.exit(2)


# -------------------------------------------------------------------------------------------------


class Entity(pygame.sprite.Sprite):
	"""Generic entity
	Returns: object
	Attributes: position_xy (starting position), file_name (sprite file name)"""
	def __init__(self, position_xy, file_name):
		pygame.sprite.Sprite.__init__(self)
		self.image = load_image(file_name)
		self.rect = self.image.get_rect()
		self.position = pygame.Vector2(position_xy)


# -------------------------------------------------------------------------------------------------


class Player(Entity):
	"""Player entity
	Returns: player object
	Functions: update
	Attributes: position_xy (starting position)"""
	def __init__(self, position_xy):
		super().__init__(position_xy, "player.png")

	def update(self, dt):
		pressed = pygame.key.get_pressed()
		move = pygame.Vector2((0, 0))

		if pressed[pygame.K_w]: move += (0, -1)
		if pressed[pygame.K_a]: move += (-1, 0)
		if pressed[pygame.K_s]: move += (0, 1)
		if pressed[pygame.K_d]: move += (1, 0)

		if move.length() > 0: move.normalize_ip()

		self.position += move * (dt/3)
		self.rect.center = self.position
