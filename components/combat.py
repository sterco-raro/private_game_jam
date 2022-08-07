# Combat system


class CombatSystem(object):
	"""Combat component: handles life, attack and defense for the parent entity
	Returns: object
	Attributes:
		_hp (int)
		max_hp (int)
		alive (bool)
		base_attack (int)
		base_defense (int)
		attack_bonus (int)
		defense_bonus (int)"""
	def __init__(self, max_hp=1, base_attack=1, base_defense=0):
		# Current state
		self.alive = True
		# Health
		self._hp = max_hp
		self.max_hp = max_hp
		# Base stats values
		self.base_attack = base_attack
		self.base_defense = base_defense
		# Passive bonuses
		self.attack_bonus = 0
		self.defense_bonus = 0

	@property
	def hp(self):
		return self._hp

	@hp.setter
	def hp(self, value):
		self._hp = max(0, min(value, self.max_hp))
		if self._hp <= 0:
			self.die()

	@property
	def attack(self):
		return self.base_attack + self.attack_bonus

	@property
	def defense(self):
		return self.base_defense + self.defense_bonus

	def is_alive(self):
		return self.alive

	def heal(self, amount):
		"""Heals the user. Clamp the value to max_hp and return the recovered amount"""
		# Exit early on full health
		if self.hp == self.max_hp:
			return 0
		new_hp = self.hp + amount
		# Limit heal to max hp
		if new_hp > self.max_hp:
			new_hp = self.max_hp
		# Apply heal and return actual amount recovered
		amount_recovered = new_hp - self.hp
		self.hp = new_hp
		return amount_recovered

	def hurt(self, amount):
		"""Damage the user, taking current defense into account"""
		if amount - self.defense <= 0:
			return 0
		# Apply actual damage
		damage = amount - self.defense
		self.hp -= damage

	def attack_target(self, target):
		"""Deal damage to a target entity"""
		if not target.combat:
			return
		# Apply damage with modified attack
		target.combat.hurt(self.attack)

	def die(self):
		"""Change user life state"""
		self.alive = False
