# Objects


try:
	import sys
	import pygame

	from entity import Entity
except ImportError as importErr:
	print("Couldn't load module. {}".format(importErr))
	sys.exit(2)


# -------------------------------------------------------------------------------------------------


class Weapon(Entity):
	"""Weapon entity, rotating around the parent
	Returns: object
	Attributes:
		parent (Entity)
		orbit_distance (int)
		original_image (pygame.Surface, image copy used in rotation transforms"""
	def __init__(self, position_xy, parent, file_name="weap_hand_L.png", orbit_distance=20, damage=1):
		super().__init__(position_xy, file_name)
		# Parent entity reference
		self.parent = parent
		# Orbit position offset from parent sprite
		self.orbit_distance = orbit_distance
		# Flip image if this weapon is on the left side of the parent
		if self.orbit_distance < 0:
			self.image = pygame.transform.flip(self.image, False, True)
		# Keep a copy of the original image for rotations
		self.original_image = self.image

	def update(self, target):
		"""Update logic based on parent and target position"""
		# Default stance
		if target is None:
			lookdir = pygame.Vector2(-1, 0)
		# Get vector pointing at current target
		else:
			lookdir = target.rect.center - self.parent.position
			lookdir = lookdir.rotate(90)
			lookdir.normalize_ip()
		# Calculate position with offset and angle to update rotation
		weapon_position = lookdir * self.orbit_distance
		rotation_angle = lookdir.angle_to((0, 1))
		# Update position and rotate sprite
		self.rect.center = self.parent.rect.center + weapon_position
		self.image = pygame.transform.rotate(self.original_image, rotation_angle)


# -------------------------------------------------------------------------------------------------


class Cursor(Entity):
	"""Cursor entity that follows mouse movement
	Returns: object
	Attributes: None"""
	def __init__(self, position_xy, file_name="cursor_crosshair.png"):
		super().__init__(position_xy, file_name)

	def update(self, camera_position):
		"""Update position based on cursor and viewport"""
		cursor_position = pygame.mouse.get_pos()
		self.rect.center = pygame.Vector2(	cursor_position[0] + camera_position[0],
											cursor_position[1] + camera_position[1])
