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
	import time
	from pygame.locals import *

	from constants import *
	from utils import load_image
	from entities import *
	from camera import SimpleCamera

except ImportError as importErr:
	print("Couldn't load module. {}".format(importErr))
	sys.exit(2)


# -------------------------------------------------------------------------------------------------


def main():
	print("\n\nPRIVATE GAME JAM. Version: {}\n".format(GAME_VERSION))

	# Variables list
	clock = None
	viewport = None
	world = None

	# Initialize screen
	pygame.init()
	viewport = pygame.display.set_mode(SCREEN_SIZE.size)#, pygame.FULLSCREEN)
	pygame.display.set_caption("Private Game Jam")

	# Hide system cursor
	pygame.mouse.set_visible(False)

	# Fill a black background as our world level
	world = pygame.Surface((1000, 1000))
	world = world.convert()
	world.fill((0, 0, 0))

	# Keep a black surface reference to clear the player position
	black_surface = world.copy()

	# Blit everything to the viewport
	viewport.blit(world, (0, 0))
	pygame.display.flip()

	# Camera viewport
	camera = SimpleCamera(GAME_WIDTH, GAME_HEIGHT)

	# Initialize entities
	player = Player(position_xy=(484, 484))
	mob1 = Mob((530,530), 250, player)
	cursor = Cursor((0,0), camera)

	hand1 = Weapon((0,0), player, 20, cursor)
	hand2 = Weapon((0,0), player, -20, cursor)

	# Rendering groups
	player_sprites = pygame.sprite.RenderPlain(mob1, player)

	# Initialize clock
	clock = pygame.time.Clock()

	# TODO TMP debug coordinates HUD
	font = pygame.font.SysFont(None, 24)
	debug_txt_coords = font.render("({}, {})".format(0, 0), True, (255,255,255))
	viewport.blit(debug_txt_coords, (20, 20))

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
		world.blit(black_surface, player.rect, player.rect)
		world.blit(black_surface, mob1.rect, mob1.rect)
		world.blit(black_surface, cursor.rect, cursor.rect)
		world.blit(black_surface, hand1.rect.inflate(6,6), hand1.rect.inflate(6,6))
		world.blit(black_surface, hand2.rect.inflate(6,6), hand2.rect.inflate(6,6))
		
		# Clear debug font position
		viewport.blit(world, (20, 20))

		# Update sprites
		player_sprites.update(dt)

		# Update camera position
		camera.update(player)

		# Update shit
		cursor.update()
		hand1.update()
		hand2.update()
		
		# render everything
		world.blit(hand1.image, hand1.rect)
		world.blit(hand2.image, hand2.rect)
		world.blit(cursor.image, cursor.rect)
		player_sprites.draw(world)

		# Draw viewport
		viewport.blit(world, (0, 0), camera.rect)

		# Draw debug text
		debug_txt_coords = font.render("({}, {})".format(font_x, font_y), True, (255,255,255))
		viewport.blit(debug_txt_coords, (20, 20))

		pygame.display.update()

		# FPS limit and keep deltatime
		dt = clock.tick(60)
		font_x = int(mob1.position[0])
		font_y = int(mob1.position[1])


# -------------------------------------------------------------------------------------------------


if __name__ == '__main__':
	main()
