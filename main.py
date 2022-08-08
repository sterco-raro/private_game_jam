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
	import pygame
	from pygame.locals import *

	from constants import *
	from entities import Player, Enemy, Heart, RandomPill
	from game_map import Tilemap
	from utils import load_image
	from components.combat import CombatSystem
except ImportError as importErr:
	print("Couldn't load module. {}".format(importErr))
	sys.exit(2)


# -------------------------------------------------------------------------------------------------


def render_basic_menu(surface, background, text_surface, text_margin_left, text_margin_top):
	"""Render a basic splash screen (background and text), wait for user input"""
	# Setup rendering
	surface.blit(background, (0, 0))
	surface.blit(text_surface, (text_margin_left, text_margin_top))
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


def main_menu(surface, background, font):
	"""Render the main menu"""
	render_basic_menu(	surface, background,
						font.render(MAIN_MENU_TEXT, True, (255, 255, 255)),
						20, VIEWPORT_HEIGHT - 40)


def game_over(surface, background, font):
	"""Render the game over screen"""
	render_basic_menu(	surface, background,
						font.render(GAME_OVER_TEXT, True, (255, 255, 255)),
						20, VIEWPORT_HEIGHT - 40)


# -------------------------------------------------------------------------------------------------


def spawn_player():
	"""Spawn the player at a defined location"""
	_combat = CombatSystem(max_hp=8, base_attack=2, base_defense=1)
	return Player(position_xy=PLAYER_SPAWN_POINT, combat=_combat)


def spawn_enemies(player, how_many=4):
	"""Spawn a number of enemies with a random position offset"""
	enemies = []
	combat = None
	chosen_entity = 0
	entities_number = len(ENEMIES)

	for n in range(how_many):
		x = 0
		y = 0
		distance_x = 0
		distance_y = 0
		position_found = False

		# Find a position for this enemy at least SPAWN_DISTANCE away from the player
		while not position_found:
			x = random.randint(TILE_SIZE, WORLD_WIDTH - TILE_SIZE)
			y = random.randint(TILE_SIZE, WORLD_HEIGHT - TILE_SIZE)

			distance_x = abs(x - player.position[0])
			distance_y = abs(y - player.position[1])

			if distance_x >= SPAWN_DISTANCE and distance_y >= SPAWN_DISTANCE:
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
	print("\n{}. Version: {}\n".format(GAME_NAME, GAME_VERSION))

	# Pygame modules
	clock 					= None	# pygame.time.Clock

	# Surfaces
	world 					= None	# pygame.Surface, holds world map
	canvas	 				= None	# pygame.Surface, used to compose game screen before blitting to the viewport
	viewport 				= None	# pygame.Surface, window screen: render things currently visible by the player

	# Loop variables
	debug_collisions 		= False	# shows collision rectangles
	first_iteration			= True 	# TODO HACK: heal player on first loop iteration (BUG: player starts with 6/8 HP)
	dt 						= 0 	# amount of time passed since last loop iteration
	events 					= None	# pygame.events queue
	redraw_world 			= False	# the world map will render on next loop iteration
	kill_count 				= 0 	# Player kills counter

	# HUD related variables
	hud_topleft 			= None	# pygame.Surface, holds the top-left section of the HUD
	hud_topright 			= None	# pygame.Surface, holds the top-right section of the HUD
	hud_topleft_text 		= None	# Formatted string container
	hud_topright_text 		= None	# Formatted string container
	hud_topright_margin 	= 0 	# Right margin for the top-right HUD

	# Initialize pygame and window
	pygame.init()
	pygame.mouse.set_visible(False)	# Hide system cursor
	viewport = pygame.display.set_mode(SCREEN_SIZE.size)#, pygame.FULLSCREEN)
	pygame.display.set_caption(WINDOW_TITLE)

	# Initialize clock (FPS limit and general-purpose timers)
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

	# Create world map and render to related surface
	tilemap = Tilemap(size=(MAP_WIDTH, MAP_HEIGHT), file_name=LEVEL_ARENA)
	tilemap.render(world, debug_collisions)

	# Initialize entities
	player = spawn_player()
	enemies = spawn_enemies(player)
	items = []

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
				# Show collision layer
				if event.key == K_k:
					debug_collisions = not debug_collisions
					redraw_world = True
				# Spawn another wave of enemies
				if event.key == K_r:
					enemies = spawn_enemies(player, how_many=random.randint(4, 8))
				# Activate god mode
				if event.key == K_g:
					player.combat.base_defense = 100

		# Clear working surface (canvas)
		canvas.blit(world, (0, 0))

		# Logic updates
		for item in items:
			item.update(tilemap.collision_map, [player] + enemies)

		for enemy in enemies:
			enemy.update(events, dt, tilemap.collision_map, player)

		player.update(dt, tilemap.collision_map, enemies, items)

		# Only draw world map when needed
		if redraw_world:
			tilemap.render(world, debug_collisions)
			redraw_world = False

		# Render sprites
		for item in items:
			item.render(canvas)

		is_dead = False
		to_remove = []
		for enemy in enemies:
			# HACK: render will return True when the enemy dies so we can erase its reference
			is_dead = enemy.render(canvas, world, debug_collisions)
			if is_dead:
				# Update counter
				kill_count += 1
				# Randomly drop a heart (50%)
				if random.randint(0, 1):
					items.append(Heart((enemy.position[0] - 48, enemy.position[1] - 48)))
				# Randomly drop a power-up pill (50%)
				if random.randint(0, 1):
					items.append(RandomPill((enemy.position[0] + 48, enemy.position[1] + 48)))
				# Store dead entity reference to remove it outside the loop (avoid weird bugs)
				to_remove.append(enemy)
		# Delete dead enemies from entities list
		for element in to_remove:
			enemies.remove(element)

		player.render(canvas, debug_collisions)

		# Done drawing stuff, blit everything to screen
		viewport.blit(canvas, (0, 0), player.camera.rect)

		# Draw HUD
		hud_topleft_text = "HP {}/{}".format(player.combat.hp, player.combat.max_hp)
		hud_topright_text = "{} Kills".format(kill_count)

		hud_topleft = font_hud.render(hud_topleft_text, True, (0, 0, 0))
		hud_topright = font_hud.render(hud_topright_text, True, (0, 0, 0))

		hud_topright_margin = font_hud.size(hud_topright_text)[0] + HUD_MARGIN

		viewport.blit(hud_topleft, (HUD_MARGIN, HUD_MARGIN))
		viewport.blit(hud_topright, (VIEWPORT_WIDTH - hud_topright_margin, HUD_MARGIN))

		# Flip the screen, limit FPS and update temporary variables (deltatime, HUD position)
		pygame.display.update()
		dt = clock.tick(60)

		# TODO HACK: heal player on first loop iteration (BUG: player starts with 6/8 HP)
		if first_iteration:
			player.combat.heal(8)
			first_iteration = False


# -------------------------------------------------------------------------------------------------


if __name__ == '__main__':
	main()
	pygame.quit()
