# Game map


try:
	import sys
	import pygame
	import numpy as np
	from constants import TILE_SIZE, TILES_INFO, DBG_COLLISION_TILES
	from utils import load_image
except ImportError as importErr:
	print("Couldn't load module. {}".format(importErr))
	sys.exit(2)


# -------------------------------------------------------------------------------------------------


class Tilemap(object):
	"""Map handler working with square tiles of TILE_SIZE pixels
	Returns: object
	Attributes:
		map (numpy array),
		size (tuple (int, int)),
		collision_map (pygame.Rects list),
		tile_floor (pygame.Surface),
		tile_wall (pygame.Surface),
		file_name (str, relative path)"""
	def __init__(self, size=(10, 20), file_name=None):
		self.map = None
		self.size = size
		self.collision_map = []
		self.file_name = file_name
		# Tileset
		self.tile_floor = load_image("floor_1.png")
		self.tile_wall = load_image("wall_1.png")
		# Load map on start when available
		if self.file_name:
			self.set_from_file(file_name)
		# Debug rendering
		self.debug_rendering = False

	def render_tile(self, surface, tile, position, show_collision):
		"""Draw a tile on a surface with given position and optional collision rect"""
		# Draw current tile on surface
		surface.blit(tile, position)
		# Draw collision layer
		if show_collision:
			pygame.draw.rect(surface, DBG_COLLISION_TILES, pygame.Rect(position, (TILE_SIZE, TILE_SIZE)), width=1)

	def render(self, surface):
		"""Draw the whole world map on the given surface. Can draw collisions layer when needed"""
		x = 0
		y = 0
		n = self.size[0]
		m = self.size[1]
		for i in range(n):
			for j in range(m):
				# Position in pixels
				x = j * TILE_SIZE
				y = i * TILE_SIZE
				# Draw correct map tile
				if self.map[i, j] == 0:
					self.render_tile(surface, self.tile_floor, (x, y), False)
				else:
					self.render_tile(surface, self.tile_wall, (x, y), self.debug_rendering)

	def rebuild_collision_map(self, data):
		"""Build a new map of collidable tiles"""
		if len(data) == 0: return
		# Reset collisions map
		self.collision_map = []
		# Build collisions map, one pygame rect for each non-walkable tile
		n = len(data[0])
		m = len(data)
		for x in range(n):
			for y in range(m):
				if data[y][x] not in TILES_INFO["walkable"]:
					self.collision_map.append(pygame.Rect(x * TILE_SIZE, y * TILE_SIZE, TILE_SIZE, TILE_SIZE))

	def set_zero(self):
		"""Reset world map with zeros"""
		self.map = np.zeros(self.size, dtype=int)

	def set_from_file(self, file_name):
		"""Load world map from disk"""
		data = []
		# Read map file into data
		with open(file_name, "r") as fin:
			for line in fin:
				data.append([ int(x) for x in line.split() ])
		# Build numpy array from file
		self.map = np.array(data, dtype=int)
		# Update collisions map
		self.rebuild_collision_map(data)

	def save_to_file(self):
		"""Store current world map on disk, appending .save to the original file name"""
		with open("{}.save".format(self.file_name), "w") as fout:
			for x in range(self.size[0]):
				for y in range(self.size[1]):
					fout.write(str(self.map[x, y]) + " ")
				fout.write("\n")
