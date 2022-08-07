# Entities


try:
	import sys
	import pygame
	from utils import load_image
	from constants import (
		DAMPING_FACTOR,
		TILES_INFO,
		WORLD_WIDTH, WORLD_HEIGHT,
		DBG_COLLISION_PLAYER, DBG_COLLISION_ENEMY
	)
	from components.combat import CombatSystem
	from components.follower_ai import FollowerAI
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
		# Update sprite rect position
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

	def check_collisions_point(self, position_xy, collisions):
		"""Check for a collision between this entity's rect and collisions rects list"""
		for rect in collisions:
			if rect.collidepoint(position_xy):
				return True
		return False

	def check_collisions_rect(self, rect):
		"""Check for a collision between this entity's rect and collisions rects list"""
		if rect.colliderect(self.rect):
			return True
		return False

	def check_collisions_rects(self, collisions):
		"""Check for a collision between this entity's rect and collisions rects list"""
		for rect in collisions:
			if rect.colliderect(self.rect):
				return True
		return False

	def clamp_to_map(self, position_xy):
		"""Clamp position_xy vector to world map area, returns the clamped vector"""
		x = min(WORLD_WIDTH - self.rect.width/2, max(0, position_xy[0]))
		y = min(WORLD_HEIGHT - self.rect.height/2, max(0, position_xy[1]))
		return pygame.Vector2(x, y)

	def move_to(self, dt, direction, collisions):
		"""Try to move the current entity toward direction vector"""
		# Normalize vector
		if direction.length() > 0:
			direction.normalize_ip()
		# Calculate new position
		new_position = self.position + direction * dt * self.speed/DAMPING_FACTOR
		# Check for possible collisions
		if self.check_collisions_point(new_position, collisions):
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
	def __init__(
		self,
		position_xy, file_name="fatso.png", speed=32,	# Entity attributes
		combat=CombatSystem()							# Player attributes
	):
		super().__init__(position_xy, file_name, speed)
		# Fighting system
		self.combat = combat
		# Equipment
		self.cursor = Cursor((0, 0))
		self.weapon_slot_left 	= Weapon((0, 0), self, orbit_distance=30)
		self.weapon_slot_right 	= Weapon((0, 0), self, orbit_distance=-30)

	def render(self, surface, show_collision_rects):
		if not surface: return
		# Draw player weapons
		surface.blit(self.weapon_slot_left.image, self.weapon_slot_left.rect)
		surface.blit(self.weapon_slot_right.image, self.weapon_slot_right.rect)
		# Draw player sprite
		surface.blit(self.image, self.rect)

		# TODO TMP DEBUG
		# Draw collision layer for each attacking hand
		if show_collision_rects:
			pygame.draw.rect(surface, DBG_COLLISION_PLAYER, self.weapon_slot_left.rect, width=1)
			pygame.draw.rect(surface, DBG_COLLISION_PLAYER, self.weapon_slot_right.rect, width=1)

		# Draw crosshair
		surface.blit(self.cursor.image, self.cursor.rect)

	def update(self, dt, collisions, camera_position, entities):
		# Mouse buttons state
		mouse_left 		= None
		mouse_middle 	= None
		mouse_right 	= None
		# Key state
		pressed = pygame.key.get_pressed()
		# Movement direction
		direction = pygame.Vector2((0, 0))
		# Get direction based on keys pressed
		if pressed[pygame.K_w] or pressed[pygame.K_UP]: 	direction += ( 0, -1)
		if pressed[pygame.K_a] or pressed[pygame.K_LEFT]: 	direction += (-1,  0)
		if pressed[pygame.K_s] or pressed[pygame.K_DOWN]: 	direction += ( 0,  1)
		if pressed[pygame.K_d] or pressed[pygame.K_RIGHT]: 	direction += ( 1,  0)
		# if pressed click sinistro: attacca col sinistro, ecc
		mouse_left, mouse_middle, mouse_right = pygame.mouse.get_pressed()
		if mouse_left: self.attack_with_slot(True, entities)
		if mouse_right: self.attack_with_slot(False, entities)
		# Move sprite in calculated direction
		self.move_to(dt, direction, collisions)
		# Update crosshair
		self.cursor.update(camera_position)
		# Update player equipment
		self.weapon_slot_left.update(self.cursor)
		self.weapon_slot_right.update(self.cursor)

	def attack_with_slot(self, left_slot, entities):
		# Check collisions between attack rect and entities
		for entity in entities:
			# Deal damage to colliding entities with the correct slot (using a slightly bigger rect)
			if left_slot:
				if (self.weapon_slot_left.rect.inflate(5, 5).colliderect(entity.rect)):
					self.combat.attack_target(entity)
			else:
				if (self.weapon_slot_right.rect.inflate(5, 5).colliderect(entity.rect)):
					self.combat.attack_target(entity)


# -------------------------------------------------------------------------------------------------


class Enemy(Entity):
	"""TODO docstring for Enemy"""
	def __init__(
		self,
		position_xy, file_name="geezer_1.png", speed=28,			# Entity attributes
		enemy_id=1, sight_radius=250, target=None, combat=CombatSystem()	# Enemy attributes
	):
		super().__init__(position_xy, file_name, speed)
		# Components
		self.combat = combat
		self.follower = FollowerAI(parent=self, sight_radius=sight_radius, target=target)
		# Attack cooldown control
		self.attacking = False
		# Attack cooldown timer
		self.ev_attack_cooldown = pygame.USEREVENT + enemy_id
		# Dead body sprite
		self.corpse = load_image("corpse_generic.png")

	def render(self, surface, dead_surface, show_collision_rects):
		# Exit early when surface is None
		if not surface: return
		# Render corpse to different surface when entity is dead
		if not self.combat.is_alive():
			dead_surface.blit(self.corpse, self.rect)
			return True
		# Draw this entity
		surface.blit(self.image, self.rect)
		# Draw collision layer
		if show_collision_rects:
			pygame.draw.rect(surface, DBG_COLLISION_ENEMY, self.rect, width=1)
		return False

	def update(self, events, dt, collisions, player):

		if not self.combat.is_alive():
			return
		if not self.follower:
			return

		for event in events:
			if event.type == self.ev_attack_cooldown:
				self.attacking = False

		# Check collision with player entity to attack (and pause follower ai)
		if not self.attacking and self.check_collisions_rect(player.rect):
			self.attacking = True
			# Restart attack cooldown
			pygame.time.set_timer(self.ev_attack_cooldown, 1000, loops=1)
			# Apply attack and stop following the player
			self.combat.attack_target(player)

		# Move entity towards player while not colliding
		self.follower.update(dt, collisions)


# -------------------------------------------------------------------------------------------------


class Weapon(Entity):
	"""Weapon entity 
	Returns: weapon object
	Functions: update
	Attributes: position_xy, parent, orbit_distance, target, file_name"""
	def __init__(self, position_xy, parent, file_name="weap_hand_L.png", orbit_distance=20, damage=1):
		super().__init__(position_xy, file_name)

		self.parent = parent						# who is using this weapon?
		self.orbit_distance = orbit_distance		# how far should the weapon orbit around the parent

		if self.orbit_distance < 0:										# if weapon is on opposite side of parent
			self.image = pygame.transform.flip(self.image, False, True)	# flip the image
		self.original_image = self.image								# save a copy of this image for rendering rotations

		self.damage = damage

	def update(self, target):
		if target is None:
			lookdir = pygame.Vector2(-1, 0)
		else:
			lookdir = target.rect.center - self.parent.position
			lookdir = lookdir.rotate(90)
			lookdir.normalize_ip()

		weapon_position = lookdir * self.orbit_distance
		rotation_angle = lookdir.angle_to((0, 1))

		self.rect.center = self.parent.rect.center + weapon_position
		self.image = pygame.transform.rotate(self.original_image, rotation_angle)


# -------------------------------------------------------------------------------------------------


class Cursor(Entity):
	"""Cursor entity that follows mouse movement
	Returns: object
	Functions: update
	Attributes: none"""
	def __init__(self, position_xy, file_name="cursor_crosshair.png"):
		super().__init__(position_xy, file_name)

	def update(self, camera_position):
		cursor_position = pygame.mouse.get_pos()
		# Update cursor position with viewport coordinates
		self.rect.center = pygame.Vector2(	cursor_position[0] + camera_position[0],
											cursor_position[1] + camera_position[1])
