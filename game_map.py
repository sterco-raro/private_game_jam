# Dungeon generator


try:
	import sys
	import random
	import pygame
	import numpy as np
	from enum import auto, Enum
	from constants import TILE_SIZE
	from utils import load_image
except ImportError as importErr:
	print("Couldn't load module. {}".format(importErr))
	sys.exit(2)


# -------------------------------------------------------------------------------------------------


class TileType(Enum):
	FLOOR = auto()
	WALL = auto()

class TileSurface(object):
	"""TODO docstring for TileSurface"""
	def __init__(self, color):
		self.image = pygame.Surface((TILE_SIZE, TILE_SIZE))
		self.image.fill(color)

# TODO docs for TILE_IMAGES
TILE_IMAGES = [
	# TileType.FLOOR: TileSurface((255, 245, 180)),
	# TileType.WALL: TileSurface((66, 66, 66)),
	TileSurface((255, 245, 180)),
	TileSurface((66, 66, 66)),
]


# -------------------------------------------------------------------------------------------------


class Tile(object):
	"""TODO docstring for Tile"""
	def __init__(
		self,
		pos_x, pos_y, size=TILE_SIZE,
		tile_type=TileType.FLOOR,
		walkable=True,
		visible=False,
		explored=False
	):
		self.position = pygame.Vector2(pos_x, pos_y)
		# Tile type enum
		self.tile_type = tile_type
		# This tile can be walked on
		self.walkable = walkable
		# Currently visible by the player
		self.visible = visible
		# Has been visited by the player
		self.explored = explored


class Tileset(object):
	"""TODO docstring for Tileset"""
	def __init__(self, file_name, size=(TILE_SIZE, TILE_SIZE), margin=1, spacing=1):
		self.file_name = file_name
		self.size = size
		self.margin = margin
		self.spacing = spacing

		self.image = load_image(file_name)
		self.rect = self.image.get_rect()

		self.tiles = []
		self.load()

	def load(self):
		self.tiles = []

		tile = None
		x0 = y0 = self.margin
		w, h = self.rect.size
		dx = self.size[0] + self.spacing
		dy = self.size[1] + self.spacing

		for x in range(x0, w, dx):
			for y in range(y0, h, dy):
				tile = pygame.Surface(self.size)
				tile.blit(self.image, (0, 0), (x, y, *self.size))
				self.tiles.append(tile)


class Tilemap(object):
	"""TODO docstring for Tilemap"""
	def __init__(self, tileset, size=(10, 20), rect=None):
		self.size = size
		self.tileset = tileset
		self.map = np.zeros(size, dtype=int)
		self.tilesmap = []

		h, w = self.size
		self.image = pygame.Surface((32*w, 32*h))
		if rect:
			self.rect = pygame.Rect(rect)
		else:
			self.rect = self.image.get_rect()

		# # Fill tilesmap with Tile() values
		# w = len(self.tileset.)

	def render(self):
		tile = None
		m, n = self.map.shape
		for i in range(m):
			for j in range(n):
				tile = self.tileset.tiles[self.map[i, j]]
				self.image.blit(tile, (j*32, i*32))

	def set_zero(self):
		self.map = np.zeros(self.size, dtype=int)
		print(self.map)
		print(self.map.shape)
		self.render()

	def set_random(self):
		n = len(self.tileset.tiles)
		self.map = np.random.randint(n, size=self.size)
		print(self.map)
		self.render()


# -------------------------------------------------------------------------------------------------


class GameMap(object):
	"""TODO docstring for GameMap"""
	def __init__(self, width, height, entities=[]):
		self.width = width
		self.height = height
		self.entities = entities
		# Fill tiles list with default values
		self.tiles = [[Tile(x, y) for x in range(width)] for y in range(height)]
		# Tile rect reference
		self.tile_rect = pygame.Rect((0, 0, TILE_SIZE, TILE_SIZE))

	def draw(self, surface, offset):
		a = 0
		for x in range(self.width):
			a = 0 if x%2 == 0 else 1
			for y in range(self.height):
				surface.blit(
					# TILE_IMAGES[self.tiles[x][y].tile_type].image.convert(), 	# Source surface
					TILE_IMAGES[a].image.convert(), 	# Source surface
					self.tiles[x][y].position + offset, 						# Destination position
					self.tile_rect		 										# Area
				)
