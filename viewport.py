# Viewport

try:
	import sys
	import pygame

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
		x = target.rect.centerx - int(self.width/2)
		y = target.rect.centery - int(self.height/2)

		x = max(0, x)
		y = max(0, y)

		x = min(1000 - self.width, x)
		y = min(1000 - self.height, y)

		self.rect = pygame.Rect(x, y, self.width, self.height)
