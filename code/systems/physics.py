import pygame
from esper import Processor, set_handler
from code.components.hitbox 	import Hitbox
from code.components.map 		import TileMap
from code.components.physics 	import PhysicsBody
from code.components.sprite 	import AnimatedSprite
from code.settings import (
	FPS_LIMIT,
	TILE_SIZE,
	VECTOR_ZERO,
)
from code.decorators import exectime


# -------------------------------------------------------------------------------------------------


class PhysicsSimulation(Processor):
	"""Simulate entities movement on a fixed timestep basis"""

	def __init__(self, bounding_rect):
		# Defaults to viewport size for the bounding rect
		if not bounding_rect:
			screen_size = pygame.display.get_surface().get_size()
			bounding_rect = (0, 0, screen_size[0], screen_size[1])

		# Map boundaries, defaults to screen boundaries
		self.min_x = bounding_rect[0]
		self.min_y = bounding_rect[1]
		self.max_x = bounding_rect[2]
		self.max_y = bounding_rect[3]

		# Tilemap component reference
		self.tilemap 			= None

		# Debug flag to toggle collision detection
		self.collisions_enabled = True

		# Physics frames handling
		# TODO COMMENT
		self.steps 			= 0
		self.max_frameskip 	= 5
		self.step_ticks 	= 1000 / FPS_LIMIT
		self.previous_ticks = pygame.time.get_ticks()

		# Event handlers
		set_handler("toggle_collisions", self.on_toggle_collisions)

	def on_toggle_collisions(self, value):
		"""Toggle collision system"""
		self.collisions_enabled = value

	def clamp_vector2_ip(self, vector, half_width, half_height):
		vector.x = round( min(self.max_x - half_width,  max(self.min_x + half_width,  vector.x)) )
		vector.y = round( min(self.max_y - half_height, max(self.min_y + half_height, vector.y)) )

	def is_valid_position(self, hitbox, position):
		"""Check map position validity and objects collisions"""

		# Move hitbox to the given position
		new_hitbox = hitbox.rect.copy()
		new_hitbox.center = ( position.x + hitbox.offset_x, position.y + hitbox.offset_y )
		new_hitbox.inflate_ip( -16, -16 )

		# Find current position grid cell
		x = int( position.x / TILE_SIZE )
		y = int( position.y / TILE_SIZE )

		# Scan map for collidable tiles
		empty_cells_layer = 0
		for layer in self.tilemap.layers:
			# Skip empty cells in the current layer
			if self.tilemap.level_data[layer][y][x] == "-1":
				empty_cells_layer += 1
				continue
			# Check if the current cell cannot be walked on
			if not self.tilemap.tileset[ self.tilemap.level_data[layer][y][x] ].walkable:
				return False

		# How many empty cells are there in (x, y), if all layers have them then we can't walk on that tile
		if empty_cells_layer == len(self.tilemap.layers):
			return False

		# TODO TMP Basic collision detection
		others = [ item[1][0].rect for item in self.world.get_components(Hitbox) if item[1][0].rect != hitbox.rect ]
		# Fake Broad phase
		collision_indexes = new_hitbox.collidelistall(others)
		if collision_indexes:
			# Fake Narrow phase
			if others[collision_indexes[0]].colliderect(new_hitbox):
				return False

		return True

	@exectime
	def process(self, dt):
		# Get map component
		if not self.tilemap:
			self.tilemap = self.world.get_component(TileMap)[0][1]

		# Update physics in multiple fixed steps
		self.steps = 0
		while pygame.time.get_ticks() > self.previous_ticks and self.steps < self.max_frameskip:

			# A PhysicsBody needs to have an AnimatedSprite and a Hitbox component too
			# TODO Hitbox may be an optional requirement later on
			for ent, (sprite, hitbox, body) in self.world.get_components( AnimatedSprite, Hitbox, PhysicsBody ):

				# Update velocity based on current movement direction (when available)
				if body.direction.length() > 0:
					# Normalize vector to guarantee that diagonal movement and linear movement have the same length
					body.direction.normalize_ip()
					# Apply acceleration: interpolate between current directional speed and body acceleration
					velocity = body.velocity.lerp( body.direction * body.speed, body.acceleration )
				else:
					# Apply friction: interpolate between a zero-length vector and body friction
					velocity = body.velocity.lerp( VECTOR_ZERO, body.friction )

				# Update position based on current velocity
				position = body.position + velocity

				# Clamp hitbox sprite to world limits
				self.clamp_vector2_ip( position, hitbox.rect.w/2, hitbox.rect.h/2 )

				# Stop the current entity before colliding with an unwalkable tile or another physics-enabled entity
				if self.collisions_enabled:
					if not self.is_valid_position( hitbox, position ):
						"""
							To implement a simple bounce effect we can simply do "velocity = -velocity"
							A better approach may be to get the impulse strength and direction and
							compute the correct bounce angle along with a realistic impulse force
						"""
						velocity = pygame.Vector2(0, 0)
						position = body.position + velocity

				# Update physic vectors
				body.velocity = velocity
				body.position = position
				# Update sprites position
				sprite.rect.center = body.position
				hitbox.rect.center = ( body.position.x + hitbox.offset_x, body.position.y + hitbox.offset_y )

			# Simulation step completed
			self.previous_ticks += self.step_ticks
			self.steps += 1
