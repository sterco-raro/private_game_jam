import random


class FollowerAI(object):
	"""TODO docstring for FollowerAI"""
	def __init__(self, parent, sight_radius=250, target=None):
		self.parent = parent
		self._target = target
		self.sight_radius = sight_radius

	@property
	def target(self):
		return self._target

	@target.setter
	def target(self, value):
		self._target = value

	def update(self, dt, collision_map):
		# TODO check performance for Vector2.magnitude()
		if not self.target:
			return
		position = (self.target.position[0] + random.randint(-120, 120),
					self.target.position[1] + random.randint(-120, 120))
		direction = position - self.parent.position
		# Move only when target is in radius
		if direction.magnitude() <= self.sight_radius:
			self.parent.move_to(dt, direction, collision_map)
