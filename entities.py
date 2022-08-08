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
		for rect in collisions:
			if rect.collidepoint(new_position):
				return
		# No collisions, update entity position
		self.position = new_position
		self.rect.center = self.position
		# Flip sprite when moving along the X axis
		self.flip_sprite(direction[0] < 0)


# -------------------------------------------------------------------------------------------------


class Player(Entity):
	"""Player entity, with combat component and manual equipment slots
	Returns: object
	Attributes:
		combat (CombatSystem)
		weapon_slot_left (Weapon)
		weapon_slot_right (Weapon)
		cursor (Cursor)
		camera (SimpleCamera"""
	def __init__(
		self,
		position_xy, file_name="fatso.png", speed=32,	# Entity attributes
		combat=CombatSystem()							# Player attributes
	):
		super().__init__(position_xy, file_name, speed)
		# Fighting system
		self.combat = combat
		# Equipment
		self.weapon_slot_left 	= Weapon((0, 0), self, orbit_distance=30)
		self.weapon_slot_right 	= Weapon((0, 0), self, orbit_distance=-30)
		# Mouse cursor
		self.cursor = Cursor((0, 0))
		# Viewport camera
		self.camera = SimpleCamera(VIEWPORT_WIDTH, VIEWPORT_HEIGHT)

	def render(self, surface, show_collision_rects):
		"""Draw the player sprite, weapons and crosshair on the given surface"""
		if not surface: return
		# Draw player weapons
		surface.blit(self.weapon_slot_left.image, self.weapon_slot_left.rect)
		surface.blit(self.weapon_slot_right.image, self.weapon_slot_right.rect)
		# Draw player sprite
		surface.blit(self.image, self.rect)
		# Draw collision layer for each attacking hand
		if show_collision_rects:
			pygame.draw.rect(surface, DBG_COLLISION_PLAYER, self.weapon_slot_left.rect, width=1)
			pygame.draw.rect(surface, DBG_COLLISION_PLAYER, self.weapon_slot_right.rect, width=1)
		# Draw crosshair
		surface.blit(self.cursor.image, self.cursor.rect)

	def update(self, dt, collisions, entities, items):
		"""Update entity logic"""
		# Mouse buttons state
		mouse_left 		= None
		mouse_middle 	= None
		mouse_right 	= None
		# Key state
		pressed = pygame.key.get_pressed()
		# Check collisions with items
		consumed_items = []
		for item in items:
			if not item.has_been_consumed() and item.rect.colliderect(self.rect):
				item.consume(self)
				consumed_items.append(item)
		# Remove consumed items from original list
		for item in consumed_items:
			items.remove(item)
		# Movement direction
		direction = pygame.Vector2((0, 0))
		# Get direction based on keys pressed
		if pressed[pygame.K_w] or pressed[pygame.K_UP]: 	direction += ( 0, -1)
		if pressed[pygame.K_a] or pressed[pygame.K_LEFT]: 	direction += (-1,  0)
		if pressed[pygame.K_s] or pressed[pygame.K_DOWN]: 	direction += ( 0,  1)
		if pressed[pygame.K_d] or pressed[pygame.K_RIGHT]: 	direction += ( 1,  0)
		# Move sprite in calculated direction
		self.move_to(dt, direction, collisions)
		# Update crosshair
		self.cursor.update(self.camera.rect.topleft)
		# Update player equipment
		self.weapon_slot_left.update(self.cursor)
		self.weapon_slot_right.update(self.cursor)
		# Update viewport
		self.camera.update(self.rect)
		# React to mouse clicks (attacks)
		mouse_left, mouse_middle, mouse_right = pygame.mouse.get_pressed()
		if mouse_left: self.attack_with_slot(True, entities)
		if mouse_right: self.attack_with_slot(False, entities)

	def attack_with_slot(self, left_slot, entities):
		"""Try to attack a colliding entity using either the left or right slot"""
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
	"""Enemy entity, with combat and basic AI component
	Returns: object
	Attributes:
		combat (CombatSystem)
		follower (FollowerAI)
		attacking (bool)
		ev_attack_cooldown(int, pygame event id)
		corpse (pygame.Surface)"""
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
		"""Draw enemy sprite or corpse. Returns True when enemy is dead"""
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
		"""Update entity logic"""
		if not self.combat.is_alive():
			return
		if not self.follower:
			return
		# Catch timer ending event for attack cooldown
		for event in events:
			if event.type == self.ev_attack_cooldown:
				self.attacking = False
		# Check collision with player entity to attack (and pause follower ai)
		if not self.attacking and self.rect.colliderect(player.rect):
			# Change state
			self.attacking = True
			# Restart attack cooldown
			pygame.time.set_timer(self.ev_attack_cooldown, 1000, loops=1)
			# Apply attack and stop following the player
			self.combat.attack_target(player)
		# Move entity towards player while not colliding
		self.follower.update(dt, collisions)


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


# -------------------------------------------------------------------------------------------------


class Heart(Entity):
	"""TODO docstring for Heart"""
	def __init__(self, position_xy, file_name="heart.png", heal_amount=1):
		super().__init__(position_xy, file_name)
		# Number of HP restored  by consuming this item
		self.heal_amount = heal_amount
		# One-time usage control
		self._consumed = False

	def has_been_consumed(self):
		"""Check whether this item has been already consumed"""
		return self._consumed

	def render(self, surface):
		"""Draw the heart entity on the given surface"""
		if self.has_been_consumed(): return
		surface.blit(self.image, self.rect)

	def update(self):
		"""Entity update logic"""
		if self.has_been_consumed(): return

	def consume(self, target):
		"""Activate item effect first time only"""
		# Only usable on combat-enabled entities
		if not target.combat:
			return
		# Don't consume when target has full hp
		if target.combat.hp == target.combat.max_hp:
			return
		# One time only
		if not self._consumed:
			self._consumed = True
			target.combat.heal(self.heal_amount)
			return True
		return False


# -------------------------------------------------------------------------------------------------


class RandomPill(Entity):
	"""TODO docstring for RandomPill"""
	def __init__(self, position_xy, file_name="pill.png", bonus_value=1):
		super().__init__(position_xy, file_name)
		self.bonus_value  = bonus_value
		# One-time usage control
		self._consumed = False
		# Combat stats that can be powered up
		self.stats = ["attack", "defense", "max_hp", "speed"]

	def has_been_consumed(self):
		"""Check whether this item has been already consumed"""
		return self._consumed

	def render(self, surface):
		"""Draw the heart entity on the given surface"""
		if self.has_been_consumed(): return
		surface.blit(self.image, self.rect)

	def update(self):
		"""Entity update logic"""
		if self.has_been_consumed(): return

	def apply_bonus(self, target):
		# Get a random stat
		stat = self.stats[random.randint(0, len(self.stats) - 1)]
		# Apply bonus
		if stat == "attack":
			target.combat.attack_bonus += self.bonus_value
		if stat == "defense":
			target.combat.defense_bonus += self.bonus_value
		if stat == "max_hp":
			target.combat.max_hp += self.bonus_value
		if stat == "speed":
			target.speed += self.bonus_value

	def consume(self, target):
		"""Activate item effect first time only"""
		# Only usable on combat-enabled entities
		if not target.combat:
			return
		# One time only
		if not self._consumed:
			self._consumed = True
			self.apply_bonus(target)
			return True
		return False
