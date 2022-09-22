from dataclasses import dataclass, field
from code.timer import Timer
from code.settings import (
	PLAYER_COOLDOWN_BOMB,
	PLAYER_DURATION_ATTACK,
	PLAYER_DURATION_HURT
)


# -------------------------------------------------------------------------------------------------


"""
	TODO FIXME

	The animation timers work well on 60 fps but need to scale when using lower values.
	On fps < 60 the animations cannot complete a full cycle

		e.g. on 10 fps the animation starts and ends with only one frame rendered
		e.g. on 30 fps the animation starts and ends with half the needed frames rendered
"""

@dataclass
class PlayerController:
	"""Handle player animations length and abilities cooldown"""

	active: 		bool = True
	timers: 		dict = field( default_factory = dict )
	cooldowns:		dict = field( default_factory = dict )

	def __post_init__(self):
		# Animations length (in milliseconds)
		self.timers = {
			"kick": Timer( PLAYER_DURATION_ATTACK ),
			"hurt": Timer( PLAYER_DURATION_HURT )
		}
		# Abilities cooldowns (in milliseconds)
		self.cooldowns = {
			"bomb": Timer( PLAYER_COOLDOWN_BOMB )
		}

	@property
	def timers_active(self):
		for timer in self.timers.values():
			if timer.active:
				return True
		return False

	def update(self):
		for key in self.timers:
			self.timers[key].update()
		for key in self.cooldowns:
			self.cooldowns[key].update()
