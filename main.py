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
	pygame.display.set_caption("Giancarlo Pazzo Sgravato")

	# Initialize clock
	clock = pygame.time.Clock()

	# Static world surface (just a splash screen as of now)
	world = load_image("background.png")
	world = pygame.transform.scale(world, (WORLD_WIDTH, WORLD_HEIGHT))

	# Holds the whole game world state
	canvas = pygame.Surface((WORLD_WIDTH, WORLD_HEIGHT)).convert()
	canvas.fill((60, 60, 60))

	# Game map
	tilemap = Tilemap(Tileset("tileset.png"), size=(MAP_WIDTH, MAP_HEIGHT))

	# Camera viewport
	camera = SimpleCamera(VIEWPORT_WIDTH, VIEWPORT_HEIGHT)

	# Initialize entities
	player = Player(position_xy=(320, 320))

	# Rendering groups
	all_sprites = pygame.sprite.RenderPlain(player)

	# Debug HUD font
	font = pygame.font.SysFont(None, 24)

	# Draw the splash screen
	viewport.blit(world, (0, 0))
	debug_txt_coords = font.render("CIAO QUESTO È UN GIOCO BELLISSIMO (PREMI INVIO)", True, (255, 255, 255))
	viewport.blit(debug_txt_coords, (VIEWPORT_WIDTH/2 - 120, VIEWPORT_HEIGHT*3/4))
	pygame.display.flip()

	# Miscellanea loop variables
	dt = 0
	font_x = 0
	font_y = 0
	events = None
	redraw_map = False
	running = True

	# Main menu
	while running:
		events = pygame.event.get()
		for event in events:
			if event.type == QUIT:
				return

			if event.type == KEYDOWN:
				if event.key == K_RETURN:
					running = False

	# Load map and render to the background
	tilemap.set_from_file("data/level.txt")
	tilemap.render(world)

	# Game loop
	while 1:
		# Manage general pygame events
		events = pygame.event.get()
		for event in events:
			if event.type == QUIT:
				return

			if event.type == KEYDOWN:
				# Reload map data
				if event.key == K_l:
					tilemap.set_from_file("data/level.txt")
					redraw_map = True
				# Save map data to file
				if event.key == K_o:
					tilemap.save_to_file()

		# Clear temporary canvas
		canvas.blit(world, (0, 0))

		# Update sprites and camera position
		# all_sprites.update()
		player.update(dt, tilemap.collision_map)
		camera.update(player)

		# Only draw world map when needed (on changes)
		if redraw_map:
			tilemap.render(world)
			redraw_map = False

		# Draw sprites on temporary canvas
		all_sprites.draw(canvas)

		# Debug collisions UI
		# for rect in tilemap.collision_map:
		# 	pygame.draw.rect(canvas, (40, 80, 200), rect, width=1)

		# Done drawing stuff, blit everything to screen
		viewport.blit(canvas, (0, 0), camera.rect)

		# Draw HUD
		debug_txt_coords = font.render("Stai qua: ({}, {})".format(font_x, font_y), True, (255, 255, 255))
		viewport.blit(debug_txt_coords, (20, 20))

		# Flip the screen, limit FPS and update temporary variables (deltatime, HUD position)
		pygame.display.update()
		dt = clock.tick(60)
		font_x = int(player.position[0])
		font_y = int(player.position[1])


# -------------------------------------------------------------------------------------------------


if __name__ == '__main__':
	main()
