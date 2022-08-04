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
	from utils import load_image, rect_eq
	from entities import *
	from camera import SimpleCamera
	from game_map import *
	from components.combat import CombatSystem

except ImportError as importErr:
	print("Couldn't load module. {}".format(importErr))
	sys.exit(2)


# -------------------------------------------------------------------------------------------------


def main_menu(surface, background, font):
	# Setup rendering
	surface.blit(background, (0, 0))
	surface.blit(
		font.render("CIAO QUESTO È UN GIOCO BELLISSIMO (PREMI SPAZIO)", True, (255, 255, 255)),
		((VIEWPORT_WIDTH/2 - 240), VIEWPORT_HEIGHT*3/4)
	)
	pygame.display.flip()
	# Loop waiting for user input
	while 1:
		for event in pygame.event.get():
			if event.type == QUIT:
				return
			if event.type == KEYDOWN:
				if event.key == K_SPACE:
					return

def game_over(surface, background, font):
	# Setup rendering
	surface.blit(background, (0, 0))
	surface.blit(
		font.render("Ce l'hai fatta!", True, (255, 255, 255)),
		((VIEWPORT_WIDTH/2 - 240), VIEWPORT_HEIGHT*3/4)
	)
	pygame.display.flip()
	# Loop waiting for user input
	while 1:
		for event in pygame.event.get():
			if event.type == QUIT:
				return
			if event.type == KEYDOWN:
				if event.key == K_SPACE:
					return


# -------------------------------------------------------------------------------------------------


def main():
	print("\n\nPRIVATE GAME JAM. Version: {}\n".format(GAME_VERSION))

	# Variables list
	clock = None
	viewport = None
	world = None

	# Initialize screen
	pygame.init()
	viewport = pygame.display.set_mode(SCREEN_SIZE.size, pygame.FULLSCREEN)
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
	mob1 = Enemy((530, 530), file_name="geezer_2.png", enemy_id=1, speed=20, target=player, combat=CombatSystem(max_hp=4, base_attack=2, base_defense=0))
	mob2 = Enemy((570, 570), file_name="barney.png", enemy_id=2, speed=26, target=player, combat=CombatSystem(max_hp=4, base_attack=3, base_defense=0))
	mob3 = Enemy((580, 580), file_name="geezer_1.png", enemy_id=3, speed=20, target=player, combat=CombatSystem(max_hp=4, base_attack=2, base_defense=0))
	mob4 = Enemy((620, 620), file_name="geezer_2.png", enemy_id=4, speed=20, target=player, combat=CombatSystem(max_hp=4, base_attack=2, base_defense=0))

	# Rendering groups
	# all_sprites = pygame.sprite.RenderPlain(mob1)
	# ui_sprites = pygame.sprite.RenderPlain()

	# HUD font
	font = pygame.font.SysFont(None, 48)
	font_menu = pygame.font.SysFont(None, 24)

	# Miscellanea loop variables
	dt 					= 0
	font_x 				= 0
	font_y 				= 0
	events 				= None
	redraw_map 			= False
	running 			= True
	hud_topleft 		= None
	# hud_topright 		= None
	# hud_bottomleft 		= None
	# hud_bottomright 	= None
	entities 			= [mob1, mob2, mob3, mob4]

	# Render main menu and wait for user input
	main_menu(viewport, splash_screen, font_menu)

	# Load map and render to the background
	tilemap.set_from_file("data/level.txt")
	tilemap.render(world)

	one_time = True

	# Game loop
	while 1:
		# Player is dead, setup game over screen
		if not player.combat.is_alive():
			game_over(viewport, splash_screen, font_menu)
			return

		# Manage general pygame events
		events = pygame.event.get()
		for event in events:
			if event.type == QUIT:
				return

			if event.type == KEYDOWN:
				if event.key == K_r:
					mob1 = Enemy((530, 530), file_name="geezer_2.png", enemy_id=1, speed=20, target=player, combat=CombatSystem(max_hp=4, base_attack=2, base_defense=0))
					mob2 = Enemy((570, 570), file_name="barney.png", enemy_id=2, speed=26, target=player, combat=CombatSystem(max_hp=4, base_attack=3, base_defense=0))
					mob3 = Enemy((580, 580), file_name="geezer_1.png", enemy_id=3, speed=20, target=player, combat=CombatSystem(max_hp=4, base_attack=2, base_defense=0))
					mob4 = Enemy((620, 620), file_name="geezer_2.png", enemy_id=4, speed=20, target=player, combat=CombatSystem(max_hp=4, base_attack=2, base_defense=0))


		# Clear working surface (canvas)
		canvas.blit(world, (0, 0))

		# Logic updates
		mob1.update(events, dt, tilemap.collision_map, player)
		mob2.update(events, dt, tilemap.collision_map, player)
		mob3.update(events, dt, tilemap.collision_map, player)
		mob4.update(events, dt, tilemap.collision_map, player)
		player.update(dt, tilemap.collision_map, camera.rect.topleft, entities)
		camera.update(player.rect)

		# Only draw world map when needed (on changes)
		if redraw_map:
			tilemap.render(world)
			redraw_map = False

		# Render sprites
		mob1.render(canvas, world)
		mob2.render(canvas, world)
		mob3.render(canvas, world)
		mob4.render(canvas, world)
		player.render(canvas)

		# Debug collisions UI
		# for rect in tilemap.collision_map:
		# 	pygame.draw.rect(canvas, (40, 80, 200), rect, width=1)

		# Done drawing stuff, blit everything to screen
		viewport.blit(canvas, (0, 0), camera.rect)

		# Draw HUD
		hud_topleft = font.render("HP: {}/{}".format(player.combat.hp, player.combat.max_hp), True, (0, 0, 0))
		viewport.blit(hud_topleft, (20, 20))

		# Flip the screen, limit FPS and update temporary variables (deltatime, HUD position)
		pygame.display.update()
		dt = clock.tick(60)
		font_x = int(player.position[0])
		font_y = int(player.position[1])

		if one_time:
			player.combat.heal(8)
			one_time = False


# -------------------------------------------------------------------------------------------------


if __name__ == '__main__':
	main()
