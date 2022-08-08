# Enemy ai component: follower


import random


class FollowerAI(object):
	"""AI basic follower implementation, move towards target with a little bit of randomness
	Returns: object
	Attributes:
		parent (Entity)
		_target (Entity)
		sight_radius (int)"""
	def __init__(self, parent, sight_radius=250, target=None):
		# AI owner
		self.parent = parent
		# Target to follow
		self._target = target
		# Activation radius
		self.sight_radius = sight_radius

	@property
	def target(self):
		return self._target

	@target.setter
	def target(self, value):
		self._target = value

	def update(self, dt, collision_map):
		"""Update position moving towards the current target"""
		if not self.target:
			return
		# Get target position with some randomness to spice it up
		position = (self.target.position[0] + random.randint(-140, 140),
					self.target.position[1] + random.randint(-140, 140))
		direction = position - self.parent.position
		# TODO check performance for Vector2.magnitude()
		# Move only when target is in radius
		if direction.magnitude() <= self.sight_radius:
			self.parent.move_to(dt, direction, collision_map)
