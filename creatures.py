# Creatures


try:
	import sys
	import random
	import pygame

	from utils import load_image
	from camera import SimpleCamera
	from constants import (
		VIEWPORT_WIDTH, VIEWPORT_HEIGHT,
		DBG_COLLISION_PLAYER, DBG_COLLISION_ENEMY,
	)
	from entity import Entity
	from objects import Weapon, Cursor
	from items import Heart, Pill, Pillbox
	from components.combat import CombatSystem
	from components.follower_ai import FollowerAI
except ImportError as importErr:
	print("Couldn't load module. {}".format(importErr))
	sys.exit(2)


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
		# Base speed value, without bonuses
		self.base_speed = speed
		# Fighting system
		self.combat = combat
		# Equipment
		self.weapon_slot_left 	= Weapon((0, 0), self, orbit_distance=30)
		self.weapon_slot_right 	= Weapon((0, 0), self, orbit_distance=-30)
		# Mouse cursor
		self.cursor = Cursor((0, 0))
		# Viewport camera
		self.camera = SimpleCamera(VIEWPORT_WIDTH, VIEWPORT_HEIGHT)

	def get_stats(self):
		"""Returns a dictionary with all the player stats: { "stat": { "base", "bonus", "icon_tag"} }"""
		return {
			"life": {
				"base": self.combat.base_max_hp,
				"bonus": self.combat.max_hp - self.combat.base_max_hp,
				"current": self.combat.hp,
				"icon_tag": "life"
			},
			"damage": {
				"base": self.combat.base_attack,
				"bonus": self.combat.attack_bonus,
				"current": self.combat.attack,
				"icon_tag": "damage"
			},
			"shield": {
				"base": self.combat.base_defense,
				"bonus": self.combat.defense_bonus,
				"current": self.combat.defense,
				"icon_tag": "shield"
			},
			"movement": {
				"base": self.base_speed,
				"bonus": self.speed - self.base_speed,
				"current": self.speed,
				"icon_tag": "movement"
			}
		}

	def render(self, surface, show_collision_rects):
		"""Draw the player sprite, weapons and crosshair on the given surface"""
		if not surface: return
		# Draw player sprite
		surface.blit(self.image, self.rect)
		# Draw player weapons
		surface.blit(self.weapon_slot_left.image, self.weapon_slot_left.rect)
		surface.blit(self.weapon_slot_right.image, self.weapon_slot_right.rect)
		# Draw collision layer for each attacking hand
		if show_collision_rects:
			pygame.draw.rect(surface, DBG_COLLISION_PLAYER, self.weapon_slot_left.rect, width=1)
			pygame.draw.rect(surface, DBG_COLLISION_PLAYER, self.weapon_slot_right.rect, width=1)
		# Draw crosshair
		surface.blit(self.cursor.image, self.cursor.rect)

	def update(self, dt, collisions, entities, items, notify_cb):
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
			if (
				not item.has_been_consumed() and
				item.rect.inflate(5, 5).colliderect(self.rect)
			):
				if item.consume(self):
					consumed_items.append(item)
					# TODO TMP FA SCHIFO
					text = ""
					item_type = type(item)
					if item_type == Heart:
						text = "Hai mangiato un cuore wow che schifo"
					elif item_type == Pill:
						text = "Questa pillola sapeva di {}".format(random.choice(["culo", "vomito", "rancore", "indifferenza", "bambini", "amore", "piedi", "politica", "cuori infranti"]))
					elif item_type == Pillbox:
						text = "Oh no troppi ingredienti"
					notify_cb(text, cooldown=2)
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
		position_xy, file_name="geezer_1.png", speed=28,					# Entity attributes
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
