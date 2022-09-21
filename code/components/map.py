from os.path import join
from code.components.sprite import StaticSprite
from code.settings import (
	MAP_TILE_DEBUG_COLOR,
	RENDERING_LAYERS,
	SPRITE_FLOOR,
	TILE_SIZE
)


# -------------------------------------------------------------------------------------------------


class Tile(StaticSprite):
	"""A map tile, basically a simple sprite with flags"""

	def __init__(
		self,
		*,
		file_name 	= SPRITE_FLOOR,
		layer 		= RENDERING_LAYERS["ground"],
		scale_size 	= (),
		spawn_point = (-1024, -1024),
		debug_color = MAP_TILE_DEBUG_COLOR,
		walkable 	= True
	):
		super().__init__(
			file_name 	= file_name,
			layer 		= layer,
			scale_size 	= scale_size,
			spawn_point = spawn_point,
			debug_color = debug_color
		)
		self.walkable = walkable
		# Other Tile-specific properties...


# -------------------------------------------------------------------------------------------------


class TileMap:
	"""Manage the current level map of tiles (each rendering layer has its own map)"""

	def __init__(self, file_name, layers, tileset):
		self.file_name 	= file_name
		self.layers 	= layers
		self.tileset 	= tileset

		self.map_width 		= 0
		self.map_height 	= 0
		self.world_width 	= 0
		self.world_height 	= 0

		# Setup map data
		self.load(self.file_name, self.layers)

	def load(self, file_name, layers):
		"""Load level data from disk"""
		# No source specified
		if not file_name or not layers: return

		# Reset current level
		self.level_data = {}

		# Update map metadata
		if file_name != self.file_name:
			self.file_name = file_name
		if layers != self.layers:
			self.layers = layers

		# Load level layer by layer
		last_layer = ""
		for layer in layers:
			last_layer = layer
			self.level_data[layer] = []
			# Build the current layer path
			full_path = join( "data", "maps", "{}_{}.txt".format(file_name, layer) )
			# Read map layer data
			with open( full_path, "r" ) as fin:
				data = None
				while line := fin.readline():
					data = line.split(" ")
					data[-1] = data[-1].replace("\n", "") # Remove newline from last element
					self.level_data[layer].append(data)
		# Get map dimensions
		self.map_height 	= len(self.level_data[last_layer])
		self.map_width 		= len(self.level_data[last_layer][0])
		self.world_height 	= self.map_height * TILE_SIZE
		self.world_width 	= self.map_width * TILE_SIZE
