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
	from utils import load_scaled_image
	from hud import Hud
	from creatures import Player, Enemy
	from items import Heart, Pill, Pillbox
	from game_map import Tilemap
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


# TODO limit player.combat bonuses to +99 (speed?)

def main():
	print("\n{}. Version: {}\n".format(GAME_NAME, GAME_VERSION))

	# Pygame modules
	clock 					= None	# pygame.time.Clock

	# Custom modules
	hud 					= None 	# Hud, handles UI rendering

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

	# Initialize pygame and window
	pygame.init()
	pygame.mouse.set_visible(False)	# Hide system cursor
	viewport = pygame.display.set_mode(SCREEN_SIZE.size)#, pygame.FULLSCREEN)
	pygame.display.set_caption(WINDOW_TITLE)

	# Initialize clock (FPS limit and general-purpose timers)
	clock = pygame.time.Clock()

	# Initialize hud module
	hud = Hud(viewport, hud_size=FONT_SIZE_HUD, color=(0, 0, 0))

	# Create menu font object
	font_menu = pygame.font.SysFont(None, FONT_SIZE_MENU)

	# Main menu and game over background surface
	menu_background = load_scaled_image("background.png", (VIEWPORT_WIDTH, VIEWPORT_HEIGHT))

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

	# Test notification
	hud.notify("AAAAAAAAAAAAAAAAAAAAAAHHHHH")

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
					player.combat.max_hp 		= 100
					player.combat.attack_bonus 	= 100
					player.combat.defense_bonus = 100
					player.combat.heal(100)
				# TODO TMP
				if event.key == K_j:
					hud.notify("HAI PREMUTO LA J?????")

		# Clear working surface (canvas)
		canvas.blit(world, (0, 0))

		# Logic updates
		for item in items:
			item.update(dt, tilemap.collision_map, player, enemies)

		for enemy in enemies:
			enemy.update(events, dt, tilemap.collision_map, player)

		player.update(dt, tilemap.collision_map, enemies, items, hud.notify)

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
				# Random item roll [0, 1)
				chance = random.random()
				# Random spawn offset
				x = enemy.position.x + (random.choice([-1, 1]) * random.randint(24, 32))
				y = enemy.position.y + (random.choice([-1, 1]) * random.randint(24, 32))
				# Pillbox (5%)
				if chance < 0.05:
					items.append(Pillbox((x, y), number_of_pills=random.randint(3, 5)))
				# Heart (20%)
				if chance < 0.2:
					items.append(Heart((x, y)))
				# Pill (30%)
				elif chance < 0.3:
					items.append(Pill((x, y)))
				# Store dead entity reference to remove it outside the loop (avoid weird bugs)
				to_remove.append(enemy)
		# Delete dead enemies from entities list
		for element in to_remove:
			enemies.remove(element)

		player.render(canvas, debug_collisions)

		# Done drawing stuff, blit everything to screen
		viewport.blit(canvas, (0, 0), player.camera.rect)

		# Draw HUD
		hud.render_hud(player.get_stats(), kill_count)

		# Flip the screen, limit FPS and update deltatime
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
	print("\n\n:(\n")
