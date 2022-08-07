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
	from entities import *
	from game_map import *
	from utils import load_image, rect_eq
	from camera import SimpleCamera
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
	# Update display
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
		font.render("CE L'HAI FATTA! (PREMI SPAZIO WOW)", True, (255, 255, 255)),
		((VIEWPORT_WIDTH/2 - 240), VIEWPORT_HEIGHT*3/4)
	)
	# Update display
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


def spawn_player():
	_combat = CombatSystem(max_hp=8, base_attack=2, base_defense=1)
	return Player(position_xy=(8 * TILE_SIZE, 8 * TILE_SIZE), combat=_combat)


def spawn_enemies(player, how_many=4):
	"""Spawn a number of enemies with a random position offset"""
	enemies = []
	combat = None
	chosen_entity = 0
	entities_number = len(ENEMIES)

	# TODO random position inside arena
	for n in range(how_many):
		x = 0
		y = 0
		distance_x = 0
		distance_y = 0
		position_found = False

		while not position_found:
			x = random.randint(TILE_SIZE, WORLD_WIDTH - TILE_SIZE)
			y = random.randint(TILE_SIZE, WORLD_WIDTH - TILE_SIZE)

			distance_x = abs(x - player.position[0])
			distance_y = abs(y - player.position[1])

			if distance_x >= 4 * TILE_SIZE and distance_y >= 4 * TILE_SIZE:
				position_found = True

		# Choose a random enemy in previously made list
		chosen_entity = ENEMIES[random.randint(0, entities_number - 1)]

		# Create combat system data
		combat = CombatSystem(	max_hp=chosen_entity["max_hp"],
								base_attack=chosen_entity["base_attack"],
								base_defense=chosen_entity["base_defense"])
		# Create enemy and append to output list
		enemies.append(Enemy(	position_xy=(x, y), file_name=chosen_entity["sprite"],
								enemy_id=n, speed=chosen_entity["speed"],
								sight_radius=chosen_entity["sight_radius"],
								target=player, combat=combat))
	return enemies


# -------------------------------------------------------------------------------------------------


def main():
	print("\n\nPRIVATE GAME JAM. Version: {}\n".format(GAME_VERSION))

	# Main() "global" variables
	clock 					= None	# pygame.time.Clock

	world 					= None	# pygame.Surface, holds world map
	canvas	 				= None	# pygame.Surface, used to compose game screen before blitting to the viewport
	viewport 				= None	# pygame.Surface, window screen: render things currently visible by the player

	debug_collisions 		= False	# shows collision rectangles
	first_iteration			= True 	# TODO HACK: heal player on first loop iteration (BUG: player starts with 6/8 HP)
	dt 						= 0 	# amount of time passed since last loop iteration
	events 					= None	# pygame.events queue
	redraw_world 			= False	# the world map will render on next loop iteration

	kill_count 				= 0 	# Player kills counter

	hud_topleft 			= None	# pygame.Surface, holds the top-left section of the HUD
	hud_topright 			= None	# pygame.Surface, holds the top-right section of the HUD
	# hud_bottomleft 			= None	# pygame.Surface, holds the bottom-left section of the HUD
	# hud_bottomright 		= None	# pygame.Surface, holds the bottom-right section of the HUD
	hud_topleft_text 		= None
	hud_topright_text 		= None
	# hud_topleft_offset 	= 0
	hud_topright_offset_x 	= 0

	# Initialize pygame and window
	pygame.init()
	pygame.mouse.set_visible(False)	# Hide system cursor
	viewport = pygame.display.set_mode(SCREEN_SIZE.size)#, pygame.FULLSCREEN)
	pygame.display.set_caption("Giancarlo Pazzo Sgravato")

	# Initialize clock (mainly FPS limit)
	clock = pygame.time.Clock()

	# Create pygame font objects
	font_hud = pygame.font.SysFont(None, FONT_SIZE_HUD)
	font_menu = pygame.font.SysFont(None, FONT_SIZE_MENU)

	# Main menu and game over background surface
	menu_background = load_image("background.png")
	menu_background = pygame.transform.scale(menu_background, (VIEWPORT_WIDTH, VIEWPORT_HEIGHT))

	# Render main menu and wait for user input
	main_menu(viewport, menu_background, font_menu)

	# Setup game surfaces
	world = pygame.Surface((WORLD_WIDTH, WORLD_HEIGHT)).convert()
	canvas = pygame.Surface((WORLD_WIDTH, WORLD_HEIGHT)).convert()

	# Camera viewport, centered on given target (in camera update function)
	camera = SimpleCamera(VIEWPORT_WIDTH, VIEWPORT_HEIGHT)

	# Create world map and render to related surface
	tilemap = Tilemap(Tileset("tileset.png"), size=(MAP_WIDTH, MAP_HEIGHT), file_name="data/level.txt")
	tilemap.render(world, debug_collisions)

	# Initialize entities
	player = spawn_player()
	enemies = spawn_enemies(player)

	# Game loop
	while 1:
		# Player is dead, setup game over screen
		if not player.combat.is_alive():
			game_over(viewport, menu_background, font_menu)
			return

		# Manage general pygame events
		events = pygame.event.get()
		for event in events:
			if event.type == QUIT:
				return

			if event.type == KEYDOWN:
				if event.key == K_k:
					debug_collisions = not debug_collisions
					redraw_world = True
				# TODO R to reset game/world state, not to spawn enemies
				# TODO add a spawner for enemy waves
				if event.key == K_r:
					enemies = spawn_enemies(player, how_many=random.randint(4, 8))

		# Clear working surface (canvas)
		canvas.blit(world, (0, 0))

		# Logic updates
		for enemy in enemies:
			enemy.update(events, dt, tilemap.collision_map, player)
		player.update(dt, tilemap.collision_map, camera.rect.topleft, enemies)
		camera.update(player.rect)

		# Only draw world map when needed
		if redraw_world:
			tilemap.render(world, debug_collisions)
			redraw_world = False

		# Render sprites
		dead = False
		for i in range(len(enemies) - 1):
			# HACK: render will return True when the enemy dies so we can erase its reference
			dead = enemies[i].render(canvas, world, debug_collisions)
			if dead:
				kill_count += 1
				enemies.pop(i)
		player.render(canvas, debug_collisions)

		# Done drawing stuff, blit everything to screen
		viewport.blit(canvas, (0, 0), camera.rect)

		# Draw HUD
		hud_topleft_text = "HP {}/{}".format(player.combat.hp, player.combat.max_hp)
		hud_topright_text = "{} Kills".format(kill_count)

		hud_topleft = font_hud.render(hud_topleft_text, True, (0, 0, 0))
		hud_topright = font_hud.render(hud_topright_text, True, (0, 0, 0))

		# hud_topleft_offset = font_hud.size(hud_topleft_text)
		hud_topright_offset_x = font_hud.size(hud_topright_text)[0] + 10

		viewport.blit(hud_topleft, (10, 10))
		viewport.blit(hud_topright, (VIEWPORT_WIDTH - hud_topright_offset_x, 10))

		# Flip the screen, limit FPS and update temporary variables (deltatime, HUD position)
		pygame.display.update()
		dt = clock.tick(60)

		# TODO HACK: 
		if first_iteration:
			player.combat.heal(8)
			first_iteration = False


# -------------------------------------------------------------------------------------------------


if __name__ == '__main__':
	main()
	pygame.quit()
