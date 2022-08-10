# Entities


try:
	import sys
	import random
	import pygame

	from constants import RECT_SIDES
	from entities import Entity

except ImportError as importErr:
	print("Couldn't load module. {}".format(importErr))
	sys.exit(2)


# -------------------------------------------------------------------------------------------------


class Consumable(Entity):
	"""Generic consumable item, can be used only once. Collides with walls and entities and can be pushed around
	Returns: object
	Attributes:
		_consumed (bool)"""
	def __init__(self, position_xy, file_name="unknown.png"):
		super().__init__(position_xy, file_name)
		# Defaults to one-time item use
		self._consumed = False

	def has_been_consumed(self):
		"""Check whether this item has been already consumed"""
		return self._consumed

	def consume(self, target):
		"""Activate item effect and consume self. Not implemented! Must be done in subclasses"""
		raise NotImplementedError("Subclasses must implement their own consume() method")

	# TODO add a bouncing effect
	def collide(self, dt, rects):
		"""Collision to enable entities to push items around (and walls to stop them)"""
		# Find first colliding entity
		index = self.rect.collidelist(rects)
		if index == -1: return

		# Get the collision rectangle
		clip = self.rect.clip(rects[index])

		# Get colliding sides
		hits = []#[edge for edge in RECT_SIDES if getattr(clip, edge) == getattr(self.rect, edge)]
		for edge in RECT_SIDES:
			if getattr(clip, edge) == getattr(self.rect, edge):
				hits.append(edge)

		# Create a new direction vector based on colliding sides
		direction = None
		hits_len = len(hits)

		# Two sides: move diagonally
		if hits_len == 2:
			if "top" in hits and "left" in hits:
				direction = pygame.Vector2(1, 1)
			elif "top" in hits and "right" in hits:
				direction = pygame.Vector2(-1, 1)
			elif "bottom" in hits and "left" in hits:
				direction = pygame.Vector2(1, -1)
			elif "bottom" in hits and "right" in hits:
				direction = pygame.Vector2(-1, -1)
		# Three sides: exclude opposite sides and move in the remaining direction
		if hits_len >= 3:
			if "top" in hits and "bottom" in hits:
				if "left" in hits:
					direction = pygame.Vector2(1, 0)
				elif "right" in hits:
					direction = pygame.Vector2(-1, 0)
			elif "left" in hits and "right" in hits:
				if "top" in hits:
					direction = pygame.Vector2(0, 1)
				elif "bottom" in hits:
					direction = pygame.Vector2(0, -1)
		# Perform movement
		if direction:
			self.move_to(dt, direction, [])

	def render(self, surface):
		"""Draw the item on the given surface"""
		if self.has_been_consumed(): return
		surface.blit(self.image, self.rect)

	def update(self, dt, collisions, player, entities):
		"""Consumable item update logic"""
		if self.has_been_consumed(): return
		# Entities can push this item around
		self.collide(dt, [player] + [e.rect for e in entities])
		# Bounce off walls
		self.collide(dt, collisions)


# -------------------------------------------------------------------------------------------------


class Heart(Consumable):
	"""Simple healing item
	Returns: object
	Attributes:
		heal_amount (int)"""
	def __init__(self, position_xy, file_name="heart.png", heal_amount=20):
		super().__init__(position_xy, file_name)
		# Number of HP restored  by consuming this item
		self.heal_amount = heal_amount

	def consume(self, target):
		"""Heal the target by heal_amount and consume self to avoid reuse"""
		# Only usable on combat-enabled entities
		if not target.combat: return
		# Don't consume when target has full hp
		if target.combat.hp == target.combat.max_hp: return
		# One time only
		if not self._consumed:
			self._consumed = True
			target.combat.heal(self.heal_amount)
			return True
		return False

	def update(self, dt, collisions, player, entities):
		"""Heart item update logic"""
		if self.has_been_consumed(): return
		# Entities can push this item around
		self.collide(dt, [player] + [e.rect for e in entities])
		# Bounce off walls
		self.collide(dt, collisions)


# -------------------------------------------------------------------------------------------------


class Pill(Consumable):
	"""Pill to power up a random stat between attack, defense, max_hp and speed
	Returns: object
	Attributes:
		bonus_value (int)"""
	def __init__(self, position_xy, file_name="pill.png", bonus_value=5):
		super().__init__(position_xy, file_name)
		# Combat stats that can be powered up
		self.stats = ["attack", "defense", "max_hp", "speed"]
		# Power up amount
		self.bonus_value = bonus_value

	def apply_bonus(self, target):
		# Get a random stat
		stat = random.choice(self.stats)
		# Apply bonus
		if stat == "attack":
			target.combat.attack_bonus += self.bonus_value
		elif stat == "defense":
			target.combat.defense_bonus += self.bonus_value
		elif stat == "max_hp":
			target.combat.max_hp += self.bonus_value
		elif stat == "speed":
			target.speed += self.bonus_value

	def consume(self, target):
		"""Activate item effect first time only"""
		# Only usable on combat-enabled entities
		if not target.combat: return
		# One time only
		if not self._consumed:
			self._consumed = True
			self.apply_bonus(target)
			return True
		return False

	def update(self, dt, collisions, player, entities):
		"""Pill item update logic"""
		if self.has_been_consumed(): return
		# Only enemies can push this item around
		self.collide(dt, [e.rect for e in entities])
		# Bounce off walls
		self.collide(dt, collisions)


# -------------------------------------------------------------------------------------------------


class Pillbox(Pill):
	"""A box of Pills, random effects (same as the base Pill)
	Returns: object
	Attributes:
		number_of_pills (int)"""
	def __init__(self, position_xy, file_name="pillbox.png", bonus_value=5, number_of_pills=3):
		super().__init__(position_xy, file_name, bonus_value)
		# How many pills this box contains
		self.number_of_pills = number_of_pills

	def consume(self, target):
		"""Activate item effect number_of_pills times (one-shot consume)"""
		# Only usable on combat-enabled entities
		if not target.combat: return
		# One time only
		if not self._consumed:
			self._consumed = True
			for n in range(self.number_of_pills):
				self.apply_bonus(target)
			return True
		return False
