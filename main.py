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
	# Hide system cursor
	pygame.mouse.set_visible(False)

	# Initialize clock
	clock = pygame.time.Clock()

	# Splash screen
	splash_screen = load_image("background.png")
	splash_screen = pygame.transform.scale(splash_screen, (VIEWPORT_WIDTH, VIEWPORT_HEIGHT))

	# Static world map
	world = pygame.Surface((WORLD_WIDTH, WORLD_HEIGHT)).convert()

	# Working canvas (World with sprites on)
	canvas = pygame.Surface((WORLD_WIDTH, WORLD_HEIGHT)).convert()

	# Game map
	tilemap = Tilemap(Tileset("tileset.png"), size=(MAP_WIDTH, MAP_HEIGHT))

	# Camera viewport
	camera = SimpleCamera(VIEWPORT_WIDTH, VIEWPORT_HEIGHT)

	# Initialize entities
	player = Player(position_xy=(320, 320))
	mob1 = Mob((530,530), 250, player)
	cursor = Cursor((0,0), camera)

	hand1 = Weapon((0,0), player, 20, cursor)
	hand2 = Weapon((0,0), player, -20, cursor)

	# Rendering groups
	all_sprites = pygame.sprite.RenderPlain(mob1)
	#ui_sprites = pygame.sprite.RenderPlain()

	# Debug HUD font
	font = pygame.font.SysFont(None, 24)

	# Draw the splash screen
	viewport.blit(splash_screen, (0, 0))
	debug_txt = font.render("CIAO QUESTO È UN GIOCO BELLISSIMO (PREMI QUALCOSA)", True, (255, 255, 255))
	viewport.blit(debug_txt, ((VIEWPORT_WIDTH/2 - 240), VIEWPORT_HEIGHT*3/4))
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

		# Clear working surface (canvas)
		canvas.blit(world, (0, 0))

		# Logic updates
		all_sprites.update(dt)
		player.update(dt, tilemap.collision_map)

		camera.update(player)
		cursor.update()

		hand1.update()
		hand2.update()

		# Only draw world map when needed (on changes)
		if redraw_map:
			tilemap.render(world)
			redraw_map = False

		# Draw sprites on temporary canvas
		all_sprites.draw(canvas)

		# Render weapons
		canvas.blit(hand1.image, hand1.rect)
		canvas.blit(hand2.image, hand2.rect)

		# Render player sprite
		canvas.blit(player.image, player.rect)

		# Render crosshair cursor
		canvas.blit(cursor.image, cursor.rect)

		# Debug collisions UI
		# for rect in tilemap.collision_map:
		# 	pygame.draw.rect(canvas, (40, 80, 200), rect, width=1)

		# Done drawing stuff, blit everything to screen
		viewport.blit(canvas, (0, 0), camera.rect)

		# Draw HUD
		debug_txt = font.render("Stai qua: ({}, {})".format(font_x, font_y), True, (255, 255, 255))
		viewport.blit(debug_txt, (20, 20))

		# Flip the screen, limit FPS and update temporary variables (deltatime, HUD position)
		pygame.display.update()
		dt = clock.tick(60)
		font_x = int(player.position[0])
		font_y = int(player.position[1])


# -------------------------------------------------------------------------------------------------


if __name__ == '__main__':
	main()
