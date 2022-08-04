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

		if pressed[pygame.K_w] or pressed[pygame.K_UP]: move += (0, -1)
		if pressed[pygame.K_a] or pressed[pygame.K_LEFT]: move += (-1, 0)
		if pressed[pygame.K_s] or pressed[pygame.K_DOWN]: move += (0, 1)
		if pressed[pygame.K_d] or pressed[pygame.K_RIGHT]: move += (1, 0)

		if move.length() > 0: move.normalize_ip()

		self.position += move * (dt/3)
		self.rect.center = self.position

class Mob(Entity):
	"""Mobile entity
	Returns: mob object
	Functions: update
	Attributes: position_xy (starting position), sight_radius, target (who is the player?)"""
	def __init__(self, position_xy, sight_radius, target):
		super().__init__(position_xy, "mob0.png")
		
		self.target = target
		self.sight_radius = sight_radius

	def update(self, dt):
		movedir = pygame.math.Vector2(self.target.position[0] - self.position.x, 
									  self.target.position[1] - self.position.y)
		if movedir.magnitude() <= self.sight_radius:
			movedir.normalize_ip()
			self.position += movedir * (dt/10)
			self.rect.center = self.position

class Weapon(Entity):
	"""Weapon entity 
	Returns: weapon object
	Functions: update
	Attributes: position_xy, user, orbit_distance, target, image"""
	def __init__(self, position_xy, user, orbit_distance=20, target=None, image="weap_hand_r.png"):
		super().__init__(position_xy, image)

		self.user = user						# who is using this weapon?
		self.orbit_distance = orbit_distance	# how far should the weapon orbit around the user
		self.target = target					# towards what will we rotate the weapon?

		if self.orbit_distance < 0:										# if weapon is on opposite side of user
			self.image = pygame.transform.flip(self.image, False, True)	# flip the image
		self.original_image = self.image								# save a copy of this image for rendering rotations

	def update(self):
		if self.target == None:
			lookdir = pygame.Vector2(-1,0)
		else:
			lookdir = pygame.Vector2(self.target.rect.center[0] - self.user.position.x, 
									 self.target.rect.center[1] - self.user.position.y)
			lookdir = lookdir.rotate(90)
			lookdir.normalize_ip()

		weapon_position = lookdir * self.orbit_distance
		rotation_angle = lookdir.angle_to((0,-1))

		self.rect.center = self.user.rect.center + weapon_position
		self.image = pygame.transform.rotate(self.original_image, rotation_angle)




# -------------------------------------------------------------------------------------------------

class Cursor(Entity):
	"""Cursor entity that follows mouse movement
	Returns: cursor object
	Functions: update
	Attributes: none"""
	def __init__(self, position_xy, viewport):
		super().__init__(position_xy, "cursor_crosshair.png")
		self.viewport = viewport

	def update(self):
		cursor_position = pygame.mouse.get_pos()
		camera_position = self.viewport.rect.topleft

		offset_cursor = (cursor_position[0] + camera_position[0],
						 cursor_position[1] + camera_position[1])

		self.rect.center = offset_cursor