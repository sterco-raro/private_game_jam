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

	def flip_sprite(self):
		self.image = pygame.transform.flip(self.image, True, False)


# -------------------------------------------------------------------------------------------------


class Player(Entity):
	"""Player entity
	Returns: player object
	Functions: update
	Attributes: position_xy (starting position)"""
	def __init__(self, position_xy):
		super().__init__(position_xy, "fatso.png")
		self.flipped = False

	def update(self, dt, collision_map):
		pressed = pygame.key.get_pressed()
		move = pygame.Vector2((0, 0))

		if pressed[pygame.K_w] or pressed[pygame.K_UP]: move += (0, -1)
		if pressed[pygame.K_a] or pressed[pygame.K_LEFT]: move += (-1, 0)
		if pressed[pygame.K_s] or pressed[pygame.K_DOWN]: move += (0, 1)
		if pressed[pygame.K_d] or pressed[pygame.K_RIGHT]: move += (1, 0)

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

		# Flip sprite when changing directions
		if move[0] < 0 and self.flipped == False:
			self.flip_sprite()
			self.flipped = True
		if move[0] > 0 and self.flipped == True:
			self.flip_sprite()
			self.flipped = False

# -------------------------------------------------------------------------------------------------


class Mob(Entity):
	"""Mobile entity
	Returns: mob object
	Functions: update
	Attributes: position_xy (starting position), sight_radius, target (who is the player?)"""
	def __init__(self, position_xy, sight_radius, target, file_name="geezer1.png"):
		super().__init__(position_xy, file_name)
		
		self.target = target
		self.sight_radius = sight_radius

	def update(self, dt):
		"""TODO check performance on magnitude()"""
		movedir = pygame.math.Vector2(self.target.position[0] - self.position.x, 
									  self.target.position[1] - self.position.y)
		if movedir.magnitude() <= self.sight_radius:
			movedir.normalize_ip()
			self.position += movedir * (dt/10)
			self.rect.center = self.position


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
		if self.target == None:
			lookdir = pygame.Vector2(-1, 0)
		else:
			lookdir = pygame.Vector2(self.target.rect.center[0] - self.user.position.x, 
									 self.target.rect.center[1] - self.user.position.y)
			lookdir = lookdir.rotate(90)
			lookdir.normalize_ip()

		weapon_position = lookdir * self.orbit_distance
		rotation_angle = lookdir.angle_to((0, 1))

		self.rect.center = self.user.rect.center + weapon_position
		self.image = pygame.transform.rotate(self.original_image, rotation_angle)


# -------------------------------------------------------------------------------------------------


class Cursor(Entity):
	"""Cursor entity that follows mouse movement
	Returns: cursor object
	Functions: update
	Attributes: none"""
	def __init__(self, position_xy, viewport, file_name="cursor_crosshair.png"):
		super().__init__(position_xy, file_name)
		self.viewport = viewport

	def update(self):
		cursor_position = pygame.mouse.get_pos()
		camera_position = self.viewport.rect.topleft

		self.rect.center = (cursor_position[0] + camera_position[0],
							cursor_position[1] + camera_position[1])
