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
	from game_map import *

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

	# Initialize clock
	clock = pygame.time.Clock()

	# Background image
	background = load_image("background.png")
	background = pygame.transform.scale(background, (1000, 1000))

	# Holds the whole game world state
	canvas = pygame.Surface((1000, 1000)).convert()
	canvas.fill((60, 60, 60))

	# Camera viewport
	camera = SimpleCamera(VIEWPORT_WIDTH, VIEWPORT_HEIGHT)

	# Initialize entities
	player = Player(position_xy=(484, 484))

	# Rendering groups
	allsprites = pygame.sprite.RenderPlain(player)

	# Debug HUD: player coordinates
	font = pygame.font.SysFont(None, 24)
	debug_txt_coords = font.render("({}, {})".format(0, 0), True, (255,255,255))
	viewport.blit(debug_txt_coords, (20, 20))

	dt = 0
	font_x = 0
	font_y = 0
	events = None

	tilemap = Tilemap(Tileset("tileset.png"))

	while 1:
		# Manage general pygame events
		events = pygame.event.get()
		for event in events:
			if event.type == QUIT:
				return

			if event.type == KEYDOWN:
				if event.key == K_r:
					tilemap.set_random()
				if event.key == K_z:
					tilemap.set_zero()

		# Clear temporary canvas
		canvas.blit(background, (0, 0))

		# Update sprites and camera position
		allsprites.update(dt)
		camera.update(player)

		tilemap.render()
		canvas.blit(tilemap.image, (256, 256))

		# Draw sprites on temporary canvas
		allsprites.draw(canvas)

		# Done drawing stuff, blit everything to screen
		viewport.blit(canvas, (0, 0), camera.rect)

		# Draw HUD
		debug_txt_coords = font.render("({}, {})".format(font_x, font_y), True, (255,255,255))
		viewport.blit(debug_txt_coords, (20, 20))

		# Flip the screen, limit FPS and update temporary variables (deltatime, HUD position)
		pygame.display.update()
		dt = clock.tick(60)
		font_x = int(player.position[0])
		font_y = int(player.position[1])


# -------------------------------------------------------------------------------------------------


if __name__ == '__main__':
	main()
