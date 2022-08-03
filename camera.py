# Viewport

try:
	import sys
	import pygame

	from constants import WORLD_WIDTH, WORLD_HEIGHT
except ImportError as importErr:
	print("Couldn't load module. {}".format(importErr))
	sys.exit(2)


# -------------------------------------------------------------------------------------------------


class SimpleCamera(object):
	def __init__(self, w, h):
		self.rect = pygame.Rect(0, 0, w, h)
		self.width = w
		self.height = h

	def update(self, target):
		# Center camera to target position
		x = target.rect.centerx - int(self.width/2)
		y = target.rect.centery - int(self.height/2)

		# Clamp scrolling to map size
		x = max(0, x) 							# left
		y = max(0, y) 							# top
		x = min(WORLD_WIDTH - self.width, x) 	# right
		y = min(WORLD_HEIGHT - self.height, y) 	# bottom

		self.rect = pygame.Rect(x, y, self.width, self.height)
