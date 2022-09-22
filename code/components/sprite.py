from os.path import join
from code.timer import Timer
from code.utils import import_folder, load_image, load_scaled_image
from code.settings import (
	ANIMATED_SPRITE_DEBUG_COLOR,
	RENDERING_LAYERS,
	STATIC_SPRITE_DEBUG_COLOR,
	SPRITE_UNKNOWN
)


# -------------------------------------------------------------------------------------------------


class StaticSprite:
	"""A simple sprite"""

	def __init__(
		self,
		*,
		file_name 	= SPRITE_UNKNOWN,
		layer 		= RENDERING_LAYERS["main"],
		scale_size 	= (),
		spawn_point = (-1024, -1024),
		debug_color = STATIC_SPRITE_DEBUG_COLOR
	):
		self.file_name 		= file_name
		self.layer 			= layer
		self.scale_size 	= scale_size
		self.spawn_point 	= spawn_point
		self.debug_color 	= debug_color

		# Load image surface from disk
		if not scale_size:
			self.image = load_image( file_name )
		else:
			self.image = load_scaled_image( file_name, scale_size )
		self.rect = self.image.get_rect( center = spawn_point )


# -------------------------------------------------------------------------------------------------


class AnimatedSprite:
	"""A sprite with animation support"""

	def __init__(
		self,
		*,
		duration 		= 0,
		folder 			= "",
		frames_table 	= {},
		layer 			= RENDERING_LAYERS["main"],
		scale_size 		= (),
		spawn_point 	= (-1024, -1024),
		speed 			= 6,
		debug_color 	= ANIMATED_SPRITE_DEBUG_COLOR,
	):
		self.duration 		= duration
		self.folder 		= folder
		self.frames_table 	= frames_table
		self.layer 			= layer
		self.scale_size 	= scale_size
		self.spawn_point 	= spawn_point
		self.speed 			= speed
		self.debug_color 	= debug_color

		# Animation controls
		self.status 			= ""
		self.frame_index 		= 0
		self.frames_table_keys 	= list(self.frames_table.keys())
		self.timer 				= Timer( self.duration )

		# Setup images
		self.load( folder )

	@property
	def completed(self):
		return self.duration and not self.timer.active

	def load(self, folder):
		"""Load all image surfaces from the given folder"""
		# No source specified
		if not folder: return

		# Update sources directory
		if folder != self.folder:
			self.folder = folder

		# Load animation surfaces from folder images
		for animation in self.frames_table_keys:
			self.frames_table[animation] = import_folder( join( folder, animation ), self.scale_size )

		# Reset controls
		self.frame_index = 0
		self.status = self.frames_table_keys[0]

		# Assign current animation frame
		self.image = self.frames_table[self.status][self.frame_index]
		self.rect = self.image.get_rect( center = self.spawn_point )

		# Start animation
		if self.duration: self.timer.activate()

	def update(self, dt):
		"""Update animation index with the current deltatime to be framerate-independent"""
		if self.duration and self.completed: return

		self.frame_index += self.speed * dt

		# Clamp frame index to obtain a circular animation
		if self.frame_index >= len(self.frames_table[self.status]):
			self.frame_index = 0

		# Update current animation frame
		old_rect = self.rect
		self.image = self.frames_table[self.status][int(self.frame_index)]
		self.rect = self.image.get_rect( center = old_rect.center )

		if self.duration: self.timer.update()
