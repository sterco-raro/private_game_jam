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

	from constants import (
		GAME_VERSION,
		GAME_WIDTH, GAME_HEIGHT,
	)
	from utils import load_image
	from entities import *

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
	screen = pygame.display.set_mode((GAME_WIDTH, GAME_HEIGHT))#, pygame.FULLSCREEN)
	pygame.display.set_caption("Private Game Jam")

	# Fill a black background
	background = pygame.Surface(screen.get_size())
	background = background.convert()
	background.fill((0, 0, 0))

	# Blit everything to the screen
	screen.blit(background, (0, 0))
	pygame.display.flip()

	# Initialize entities
	# player = Player((GAME_WIDTH//2 - 16, GAME_HEIGHT//2 - 16), 8)
	player = Player(position_xy=(128, 128))

	# Rendering groups
	player_sprites = pygame.sprite.RenderPlain(player)

	# Initialize clock
	clock = pygame.time.Clock()

	dt = 0
	events = None

	while 1:
		events = pygame.event.get()

		for event in events:
			if event.type == QUIT:
				return

		# Clear current player position
		screen.blit(background, player.rect, player.rect)
		# Update positions
		player_sprites.update(dt)
		# Re-draw things on screen
		player_sprites.draw(screen)
		pygame.display.update()

		# FPS limit and keep deltatime
		dt = clock.tick(60)


# -------------------------------------------------------------------------------------------------


if __name__ == '__main__':
	main()
