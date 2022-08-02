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
	screen = pygame.display.set_mode((GAME_WIDTH, GAME_HEIGHT))
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
	player = Player(position_xy=(10, 10), step=5)

	# Rendering groups
	player_sprites = pygame.sprite.RenderPlain(player)

	# Initialize clock
	clock = pygame.time.Clock()

	while 1:
		# FPS limit
		clock.tick(60)

		for event in pygame.event.get():
			if event.type == QUIT:
				return

			elif event.type == KEYDOWN:
				if event.key == K_a:
					player.change_direction_x(-1)
				if event.key == K_d:
					player.change_direction_x(1)
				if event.key == K_w:
					player.change_direction_y(-1)
				if event.key == K_s:
					player.change_direction_y(1)

			elif event.type == KEYUP:
				if event.key == K_a:
					player.change_direction_x(1)
				if event.key == K_d:
					player.change_direction_x(-1)
				if event.key == K_w:
					player.change_direction_y(1)
				if event.key == K_s:
					player.change_direction_y(-1)

		# Clear current player position
		screen.blit(background, player.rect, player.rect)
		# Update positions
		player.update()
		# Re-draw things on screen
		player_sprites.draw(screen)

		pygame.display.flip()


# -------------------------------------------------------------------------------------------------


if __name__ == '__main__':
	main()
