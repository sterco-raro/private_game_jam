# Entities


try:
	import sys
	import pygame

	from utils import load_image
	from constants import TILES_INFO, WORLD_WIDTH, WORLD_HEIGHT

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

	def update(self, dt, collision_map):
		pressed = pygame.key.get_pressed()
		move = pygame.Vector2((0, 0))

		if pressed[pygame.K_w]: move += (0, -1)
		if pressed[pygame.K_a]: move += (-1, 0)
		if pressed[pygame.K_s]: move += (0, 1)
		if pressed[pygame.K_d]: move += (1, 0)

		if move.length() > 0: move.normalize_ip()

		# Clamp player movement to map size
		newposition = self.position + move * (dt/3)
		x = min(WORLD_WIDTH - self.rect.width/2, max(0, newposition[0]))
		y = min(WORLD_HEIGHT - self.rect.height/2, max(0, newposition[1]))

		# Check for possible collisions in the new position
		for rect in collision_map:
			if rect.collidepoint(x, y):
				return

		# No collisions, update player position
		self.position = pygame.Vector2((x, y))
		self.rect.center = self.position
