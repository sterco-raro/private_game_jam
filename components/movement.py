# Movement component


try:
	import sys
	import pygame
	from dataclasses import dataclass

	from constants import DAMPING_FACTOR
except ImportError as importErr:
	print("Couldn't load module. {}".format(importErr))
	sys.exit(2)


# -------------------------------------------------------------------------------------------------

@dataclass
class Movement(object):
	"""Movement component: position and velocity manager
	Returns: object
	Attributes:
		speed (int)
		position (pygame.Vector2)
		damping_factor (int)"""
	speed: int = 32
	position: pygame.Vector2 = pygame.Vector2(0, 0)
	direction: pygame.Vector2 = pygame.Vector2(0, 0)
	damping_factor: int = DAMPING_FACTOR
