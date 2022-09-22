from pygame import Rect
from code.settings import HITBOX_DEBUG_COLOR, TILE_SIZE


# -------------------------------------------------------------------------------------------------


class Hitbox:
	"""Rectangle used for collision detection"""

	def __init__(
		self,
		*,
		offset_x 		= 0, 					# pixels
		offset_y 		= 0, 					# pixels
		scale_factor_x 	= 0, 					# (%)
		scale_factor_y 	= 0, 					# (%)
		debug_color 	= HITBOX_DEBUG_COLOR, 	# (r, g, b)
		reference_rect 	= Rect(-1024, -1024, TILE_SIZE, TILE_SIZE)
	):
		self.offset_x 		= offset_x
		self.offset_y 		= offset_y
		self.scale_factor_x = scale_factor_x
		self.scale_factor_y = scale_factor_y
		self.debug_color 	= debug_color
		self.reference_rect = reference_rect

		# Rectangle used for collision detection
		self.rect = None

		# Compute rectangle inflation values
		inflation_x = 0
		inflation_y = 0
		if scale_factor_x != 0: inflation_x = int(self.reference_rect.w * self.scale_factor_x/100)
		if scale_factor_y != 0: inflation_y = int(self.reference_rect.h * self.scale_factor_y/100)

		# Create hitbox rectangle
		self.rect = self.reference_rect.inflate( inflation_x, inflation_y )

		# Set hitbox offset
		self.rect.centerx += self.offset_x
		self.rect.centery += self.offset_y
