# Health component


try:
	from dataclasses import dataclass
except ImportError as importErr:
	print("Couldn't load module. {}".format(importErr))
	sys.exit(2)


# -------------------------------------------------------------------------------------------------

@dataclass
class Health(object):
	"""Health component: HP handler
	Returns: object
	Attributes:
		_hp (int)
		max_hp (int)
		alive (bool)"""
	max_hp: int = 1

	def __post_init__(self):
		self._alive = True
		self._hp = self.max_hp
		self.base_max_hp = self.max_hp

	@property
	def hp(self):
		return self._hp

	@hp.setter
	def hp(self, value):
		self._hp = max(0, min(value, self.max_hp))
		if self._hp <= 0:
			self.die()

	@property
	def alive(self):
		return self._alive

	def has_full_hp(self):
		return self.hp == self.max_hp

	def heal(self, amount):
		"""Heals the user. Clamp the value to max_hp and return recovered amount"""
		# Exit early on full health
		if self.hp == self.max_hp:
			return 0
		# Exit early if already dead
		if not self.is_alive():
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
		"""Damage the user. Returns damage amount"""
		# Amount must be a positive, non-zero integer
		if amount <= 0:
			return 0
		# Exit early if already dead
		if not self.is_alive():
			return 0
		# Apply actual damage
		self.hp -= amount
		return amount

	def die(self):
		"""Change user life state"""
		if self.hp != 0:
			self.hp = 0
		self._alive = False
