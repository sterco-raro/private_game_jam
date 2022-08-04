# Dungeon generator


try:
	import sys
	import random
	import pygame
	import numpy as np
	from enum import auto, Enum
	from constants import TILE_SIZE, TILES_INFO
	from utils import load_image
except ImportError as importErr:
	print("Couldn't load module. {}".format(importErr))
	sys.exit(2)


# -------------------------------------------------------------------------------------------------


class Tileset(object):
	"""Load and holds a tileset from a png image"""
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


# -------------------------------------------------------------------------------------------------


class Tilemap(object):
	"""TODO docstring for Tilemap"""
	def __init__(self, tileset, size=(10, 20)):
		self.size = size
		self.tileset = tileset
		self.map = None
		self.collision_map = []

		self.tile_floor = load_image("floor_1.png")
		self.tile_wall = load_image("wall_1.png")

	def rebuild_collision_map(self, data):
		# Exit early when data is empty
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

	def render(self, surface):
		tile = None
		n = self.size[0]
		m = self.size[1]
		for i in range(n):
			for j in range(m):
#				tile = self.tileset.tiles[self.map[i, j]]
				if self.map[i, j] == 7:
					tile = self.tile_floor
				else:
					tile = self.tile_wall
				surface.blit(tile, (j * TILE_SIZE, i * TILE_SIZE))

	def set_zero(self):
		self.map = np.zeros(self.size, dtype=int)

	def set_random(self):
		self.map = np.random.randint(len(self.tileset.tiles), size=self.size)

	def set_from_file(self, file_name):
		data = []
		with open(file_name, "r") as fin:
			for line in fin:
				data.append([ int(x) for x in line.split() ])
		self.map = np.array(data, dtype=int)
		self.rebuild_collision_map(data)

	def save_to_file(self):
		with open("data/level.txt", "w") as fout:
			for x in range(self.size[0]):
				for y in range(self.size[1]):
					fout.write(str(self.map[x, y]) + " ")
				fout.write("\n")
