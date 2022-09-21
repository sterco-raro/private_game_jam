from dataclasses import dataclass
from pygame import Rect
from code.settings import VIEWPORT_WIDTH, VIEWPORT_HEIGHT


# -------------------------------------------------------------------------------------------------


@dataclass( kw_only = True )
class CameraFollow:
	"""Viewport camera attached to a game object"""

	target: object 						# An object with a rect property (pygame.Rect)
	width: 	int 	= VIEWPORT_WIDTH
	height: int 	= VIEWPORT_HEIGHT

	def __post_init__(self):
		self.rect = Rect( 0, 0, self.width, self.height )
