# Entities


try:
	import sys
	import pygame
	from utils import load_image
	from constants import (
		DAMPING_FACTOR,
		TILES_INFO,
		WORLD_WIDTH, WORLD_HEIGHT
	)
except ImportError as importErr:
	print("Couldn't load module. {}".format(importErr))
	sys.exit(2)


# -------------------------------------------------------------------------------------------------


class Entity(pygame.sprite.Sprite):
	"""Generic entity
	Returns: object
	Attributes: position_xy (starting position), file_name (sprite file name)"""
	def __init__(self, position_xy, file_name, speed=32):
		pygame.sprite.Sprite.__init__(self)
		# Sprite
		self.image = load_image(file_name)
		self.rect = self.image.get_rect()
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

	def check_collisions(self, position_xy, collision_map):
		"""Check for a collision between this entity's rect and collision_map list"""
		for rect in collision_map:
			if rect.collidepoint(position_xy):
				return True
		return False

	def clamp_to_map(self, position_xy):
		"""Clamp position_xy vector to world map area, returns the clamped vector"""
		x = min(WORLD_WIDTH - self.rect.width/2, max(0, position_xy[0]))
		y = min(WORLD_HEIGHT - self.rect.height/2, max(0, position_xy[1]))
		return pygame.Vector2(x, y)

	def move_to(self, dt, direction, collision_map):
		"""Try to move the current entity toward direction vector"""
		# Normalize vector
		if direction.length() > 0:
			direction.normalize_ip()
		# Calculate new position
		new_position = self.position + direction * dt * self.speed/DAMPING_FACTOR
		# Check for possible collisions
		if self.check_collisions(new_position, collision_map):
			return
		# No collisions, update entity position
		self.position = new_position
		self.rect.center = self.position
		# Flip sprite when moving along the X axis
		self.flip_sprite(direction[0] < 0)


# -------------------------------------------------------------------------------------------------


class Player(Entity):
	"""Player entity
	Returns: player object
	Functions: update
	Attributes: /"""
	def __init__(self, position_xy, file_name="fatso.png", speed=32):
		super().__init__(position_xy, file_name, speed)

	def update(self, dt, collision_map):
		# Key state
		pressed = pygame.key.get_pressed()
		# Movement direction
		direction = pygame.Vector2((0, 0))
		# Get direction based on keys pressed
		if pressed[pygame.K_w] or pressed[pygame.K_UP]: 	direction += ( 0, -1)
		if pressed[pygame.K_a] or pressed[pygame.K_LEFT]: 	direction += (-1,  0)
		if pressed[pygame.K_s] or pressed[pygame.K_DOWN]: 	direction += ( 0,  1)
		if pressed[pygame.K_d] or pressed[pygame.K_RIGHT]: 	direction += ( 1,  0)
		# Move sprite in calculated direction
		self.move_to(dt, direction, collision_map)


# -------------------------------------------------------------------------------------------------


class Follower(Entity):
	"""Mobile follower entity
	Returns: object
	Functions: update
	Attributes: position_xy (starting position), sight_radius, target (who is the player?)"""
	def __init__(self, position_xy, file_name="geezer1.png", speed=32, sight_radius=250, target=None):
		super().__init__(position_xy, file_name, speed)
		self.target = target
		self.sight_radius = sight_radius

	def update(self, dt, collision_map):
		# TODO check performance on magnitude()
		direction = self.target.position - self.position
		# Move only when target is in radius
		if direction.magnitude() <= self.sight_radius:
			self.move_to(dt, direction, collision_map)


# -------------------------------------------------------------------------------------------------


class Weapon(Entity):
	"""Weapon entity 
	Returns: weapon object
	Functions: update
	Attributes: position_xy, user, orbit_distance, target, file_name"""
	def __init__(self, position_xy, user, orbit_distance=20, target=None, file_name="weap_hand_L.png"):
		super().__init__(position_xy, file_name)

		self.user = user						# who is using this weapon?
		self.orbit_distance = orbit_distance	# how far should the weapon orbit around the user
		self.target = target					# towards what will we rotate the weapon?

		if self.orbit_distance < 0:										# if weapon is on opposite side of user
			self.image = pygame.transform.flip(self.image, False, True)	# flip the image
		self.original_image = self.image								# save a copy of this image for rendering rotations

	def update(self):
		if self.target is None:
			lookdir = pygame.Vector2(-1, 0)
		else:
			lookdir = self.target.rect.center - self.user.position
			lookdir = lookdir.rotate(90)
			lookdir.normalize_ip()

		weapon_position = lookdir * self.orbit_distance
		rotation_angle = lookdir.angle_to((0, 1))

		self.rect.center = self.user.rect.center + weapon_position
		self.image = pygame.transform.rotate(self.original_image, rotation_angle)


# -------------------------------------------------------------------------------------------------


class Cursor(Entity):
	"""Cursor entity that follows mouse movement
	Returns: object
	Functions: update
	Attributes: none"""
	def __init__(self, position_xy, viewport, file_name="cursor_crosshair.png"):
		super().__init__(position_xy, file_name)
		# Camera
		self.viewport = viewport

	def update(self):
		cursor_position = pygame.mouse.get_pos()
		camera_position = self.viewport.rect.topleft
		# Update cursor position with viewport coordinates
		self.rect.center = pygame.Vector2(	cursor_position[0] + camera_position[0],
											cursor_position[1] + camera_position[1])
