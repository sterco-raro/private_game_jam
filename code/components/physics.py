from dataclasses import dataclass
from pygame.math import Vector2
from code.settings import (
	ACCELERATION_BASE_FLOOR,
	FRICTION_BASE_FLOOR,
	SPEED_BASE,
	SPEED_BASE_FACTOR,
	SPEED_MAX
)


# -------------------------------------------------------------------------------------------------


@dataclass( kw_only = True )
class PhysicsBody:
	"""Manage object movement in the physics simulation"""

	_speed:			float = SPEED_BASE
	_speed_factor:	float = SPEED_BASE_FACTOR
	friction:		float = FRICTION_BASE_FLOOR
	acceleration:	float = ACCELERATION_BASE_FLOOR
	direction:		Vector2 = Vector2(0, 0)
	position: 		Vector2 = Vector2(0, 0)
	velocity: 		Vector2 = Vector2(0, 0)

	@property
	def speed(self):
		return self._speed * self._speed_factor

	@speed.setter
	def speed(self, value):
		# Clamp value to desired interval: [0, SPEED_MAX]
		self._speed = max( 0, min( SPEED_MAX, value ) )
