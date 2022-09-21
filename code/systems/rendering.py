import pygame
from esper import Processor, set_handler
from code.components.camera import CameraFollow
from code.components.hitbox import Hitbox
from code.components.map 	import TileMap
from code.components.sprite import AnimatedSprite, StaticSprite
from code.settings import (
	RENDERING_LAYERS,
	TILE_SIZE,
)
from code.decorators import exectime


# -------------------------------------------------------------------------------------------------


class LayeredRendering(Processor):
	"""A simple layered renderer (y-sorting, layered map caching, only draw elements inside view)"""

	def __init__(self, scene_name, world_width, world_height):
		# World identifier
		self.scene_name = scene_name
		# Get a reference to the active display
		self.screen 	= pygame.display.get_surface()

		# Black surface to clear the screen
		self.background = pygame.Surface( (world_width, world_height) ).convert()
		# Working canvas for sprite rendering
		self.canvas 	= pygame.Surface( (world_width, world_height) ).convert()

		# A canvas dictionary for map layers surfaces to avoid unnecessary blits
		self.map_canvases = {}

		# Viewport component reference
		self.camera 	= None
		# Tilemap component reference
		self.tilemap 	= None

		# Flags
		self.debug 		= False # Activate debug rectangles (sprite, hitbox)
		self.redraw_map = True 	# Update the working canvas

		# Event handlers
		set_handler( "scene_change", self.on_scene_change )
		set_handler( "toggle_debug", self.on_toggle_debug )

	def on_scene_change(self, name):
		"""Notify the need to update this menu UI"""
		if name == self.scene_name: self.redraw_map = True

	def on_toggle_debug(self, value):
		"""Toggle debug routines"""
		self.debug = value
		self.redraw_map = True

	def init_static_map_surfaces(self):
		"""Create one surface for each map layer, to hold static elements until the next change"""
		if not self.tilemap: return

		self.map_canvases = {}
		for layer in self.tilemap.layers:
			# Skip main layer because its elements are rendered as sprites
			if layer == "main": continue
			# Create a surface for each layer with per-pixel alpha to enable layered rendering
			self.map_canvases[layer] = pygame.Surface(
				( self.tilemap.world_width, self.tilemap.world_height ),
				flags = pygame.SRCALPHA
			).convert_alpha()

	@exectime
	def process(self, dt):
		# Get camera component
		if not self.camera:
			self.camera = self.world.get_component(CameraFollow)[0][1]

		# Get map component
		if not self.tilemap:
			self.tilemap = self.world.get_component(TileMap)[0][1]
			self.init_static_map_surfaces()

		# Clear the screen
		self.canvas.blit(self.background, (0, 0))

		# Combine Static and Animated sprites for rendering
		y_sorted_sprites = sorted(
			self.world.get_component( StaticSprite ) + self.world.get_component( AnimatedSprite ),
			key = lambda sprite: sprite[1].rect.centery
		)

		# Build the working canvas
		for layer_name, layer_value in RENDERING_LAYERS.items():

			# Draw map layers, except for the "main" one (map elements on that layer are implemented as StaticSprite)
			if layer_name != "main" and layer_name in self.tilemap.layers:

				# Rebuild this layer's static map
				if self.redraw_map:
					# Iterate tiles and draw them
					cell_value = None
					for row in range(self.tilemap.map_height):
						for col in range(self.tilemap.map_width):
							cell_value = self.tilemap.level_data[layer_name][row][col]
							# Skip empty cells
							if cell_value == "-1": continue
							# Map grid position to world position
							tile_rect = pygame.Rect( col * TILE_SIZE, row * TILE_SIZE, TILE_SIZE, TILE_SIZE )

							# Render cell
							self.map_canvases[layer_name].blit( self.tilemap.tileset[cell_value].image, tile_rect )
							# Render debug frames
							if self.debug:
								pygame.draw.rect(
									self.map_canvases[layer_name],
									self.tilemap.tileset[cell_value].debug_color,
									tile_rect,
									width = 1
								)

				# Render this layer's static map
				self.canvas.blit( self.map_canvases[layer_name], (0, 0) )

			# Draw sprites
			for ent, sprite in y_sorted_sprites:
				# Skip out-of-view elements
				if sprite.rect.clip(self.camera.rect).size == (0, 0): continue
				# Render the current layer of sprites
				if sprite.layer == layer_value:
					self.canvas.blit(sprite.image, sprite.rect)
					# Render debug frames
					if self.debug:
						# Sprite surface
						pygame.draw.rect( self.canvas, sprite.debug_color, sprite.rect, width = 2 )
						# Related hitbox (when available)
						hitbox = self.world.try_component( ent, Hitbox )
						if hitbox:
							pygame.draw.rect( self.canvas, hitbox.debug_color, hitbox.rect, width = 2 )

		# Stop map surfaces construction once done
		if self.redraw_map: self.redraw_map = False

		# Blit everything to the screen
		self.screen.blit(self.canvas, (0, 0), self.camera.rect)
