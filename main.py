#
# Private Game Jam
# Theme: Salto nel vuoto
#
# Authors:
#	unarmedpile@gmail.com
#	serviceoftaxi@gmail.com
#


try:
	import sys
	import random
	import math
	import os
	import pygame
	from pygame.locals import *

	from utils import load_image
	from constants import (
		GAME_VERSION,
		GAME_WIDTH, GAME_HEIGHT,
	)

except ImportError as importErr:
	print("Couldn't load module. {}".format(importErr))
	sys.exit(2)


# -------------------------------------------------------------------------------------------------


def main():
	print("\n\nPRIVATE GAME JAM. Version: {}\n".format(GAME_VERSION))

	# Variables list
	clock = None
	screen = None
	background = None

	# Initialize screen
	pygame.init()
	screen = pygame.display.set_mode((GAME_WIDTH, GAME_HEIGHT))
	pygame.display.set_caption("Private Game Jam")

	# Fill a black background
	background = pygame.Surface(screen.get_size())
	background = background.convert()
	background.fill((0, 0, 0))

	# Blit everything to the screen
	screen.blit(background, (0, 0))
	pygame.display.flip()

	# Initialize clock
	clock = pygame.time.Clock()

	while 1:
		# FPS limit
		clock.tick(60)

		for event in pygame.event.get():
			if event.type == QUIT:
				return

		pygame.display.flip()


# -------------------------------------------------------------------------------------------------


if __name__ == '__main__':
	main()
