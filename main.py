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

	from constants import *
	from utils import load_image
	from entities import *
	from viewport import SimpleCamera

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
	screen = pygame.display.set_mode(SCREEN_SIZE.size)#, pygame.FULLSCREEN)
	pygame.display.set_caption("Private Game Jam")

	# Fill a black background
	background = pygame.Surface((1000, 1000))
	background = background.convert()
	background.fill((0, 0, 0))

	# TODO TMP draw green stars on screen
	for _ in range(3000):
		x, y = random.randint(0, 1000), random.randint(0, 1000)
		pygame.draw.rect(background, pygame.Color('green'), (x, y, 2, 2))
	black_surface = background.copy()

	# Blit everything to the screen
	screen.blit(background, (0, 0))
	pygame.display.flip()

	# Camera viewport
	camera = SimpleCamera(GAME_WIDTH, GAME_HEIGHT)

	# Initialize entities
	player = Player(position_xy=(484, 484))

	# Rendering groups
	player_sprites = pygame.sprite.RenderPlain(player)

	# Initialize clock
	clock = pygame.time.Clock()

	# TODO TMP debug coordinates HUD
	font = pygame.font.SysFont(None, 24)
	debug_txt_coords = font.render("({}, {})".format(0, 0), True, (255,255,255))
	screen.blit(debug_txt_coords, (20, 20))

	debug_txt_ciao = font.render("CIAO", True, (255,255,255))
	screen.blit(debug_txt_ciao, (400, 20))

	dt = 0
	font_x = 0
	font_y = 0
	events = None

	while 1:
		events = pygame.event.get()

		for event in events:
			if event.type == QUIT:
				return

		# Clear current player position
		background.blit(black_surface, player.rect, player.rect)
		# Clear debug font position
		screen.blit(background, (20, 20))
		# Update sprites
		player_sprites.update(dt)

		# Re-draw things on screen
		player_sprites.draw(background)

		# Update camera position
		camera.update(player)
		# Draw viewport
		screen.blit(background, (0, 0), camera.rect)

		# Draw debug text
		debug_txt_coords = font.render("({}, {})".format(font_x, font_y), True, (255,255,255))
		screen.blit(debug_txt_coords, (20, 20))

		debug_txt_ciao = font.render("CIAO", True, (255,255,255))
		screen.blit(debug_txt_ciao, (400, 20))

		pygame.display.update()

		# FPS limit and keep deltatime
		dt = clock.tick(60)
		font_x = int(player.position[0])
		font_y = int(player.position[1])


# -------------------------------------------------------------------------------------------------


if __name__ == '__main__':
	main()
