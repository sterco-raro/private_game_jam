# Entities


try:
	import sys
	import random
	import pygame

	from utils import load_image
	from camera import SimpleCamera
	from constants import (
		DAMPING_FACTOR,
		TILES_INFO,
		WORLD_WIDTH, WORLD_HEIGHT,
		VIEWPORT_WIDTH, VIEWPORT_HEIGHT,
		DBG_COLLISION_PLAYER, DBG_COLLISION_ENEMY,
	)
	from components.combat import CombatSystem
	from components.follower_ai import FollowerAI

except ImportError as importErr:
	print("Couldn't load module. {}".format(importErr))
	sys.exit(2)


# -------------------------------------------------------------------------------------------------


class Entity(pygame.sprite.Sprite):
	"""Generic entity with a sprite, movement and flipping mechanics
	Returns: object
	Attributes:
		image (pygame.Surface),
		rect (pygame.Rect),
		speed (int),
		position (pygame.Vector2),
		flipped (bool)"""
	def __init__(self, position_xy, file_name, speed=32):
		pygame.sprite.Sprite.__init__(self)
		# Sprite
		self.image = load_image(file_name)
		self.rect = self.image.get_rect()
		# Initialize sprite rect position
		self.rect.center = position_xy
		# Movement
		self.speed = speed
		self.position = pygame.Vector2(position_xy)
		# Flip sprite control
		self.flipped = False

	def flip_sprite(self, is_moving_left):
		"""Flip sprite when changing directions"""
		if is_moving_left and not self.flipped:
			self.image = pygame.transform.flip(self.image, True, False)
			self.flipped = True
		elif not is_moving_left and self.flipped:
			self.image = pygame.transform.flip(self.image, True, False)
			self.flipped = False

	def clamp_to_map(self, position):
		"""Clamp position vector to world map area, returns the clamped vector"""
		x = min(WORLD_WIDTH - self.rect.width/2, max(0, position.x))
		y = min(WORLD_HEIGHT - self.rect.height/2, max(0, position.y))
		return pygame.Vector2(x, y)

	def move_to(self, dt, direction, collisions):
		"""Try to move the current entity toward direction vector"""
		# Normalize vector
		if direction.length() > 0:
			direction.normalize_ip()
		# Calculate new position
		new_position = self.clamp_to_map(self.position + direction * dt * self.speed/DAMPING_FACTOR)
		# Check for possible collisions
		for rect in collisions:
			if rect.collidepoint(new_position):
				return
		# No collisions, update entity position
		self.position = new_position
		self.rect.center = self.position
		# Flip sprite when moving along the X axis
		self.flip_sprite(direction[0] < 0)

