# Gamae constants


import pygame


# General
GAME_NAME = "PrivateGameJam Pazzissima"
GAME_VERSION = "0.1"
WINDOW_TITLE = GAME_NAME

RESOURCES_FOLDER = "data"

# Window
VIEWPORT_WIDTH = 640
VIEWPORT_HEIGHT = 480

SCREEN_SIZE = pygame.Rect((0, 0, VIEWPORT_WIDTH, VIEWPORT_HEIGHT))

# Camera
CAMERA_SMOOTHNESS = 0.05

# HUD
FONT_SIZE_HUD = 48
FONT_SIZE_MENU = 24

HUD_MARGIN = 10

MAIN_MENU_TEXT = "CIAO QUESTO È UN GIOCO BELLISSIMO (WOW PREMI SPAZIO)"
GAME_OVER_TEXT = "CE L'HAI FATTA! (PREMI SPAZIO WOW)"

# Map
TILE_SIZE = 48

MAP_WIDTH = 16
MAP_HEIGHT = 16

WORLD_WIDTH = MAP_WIDTH * TILE_SIZE
WORLD_HEIGHT = MAP_HEIGHT * TILE_SIZE

TILES_INFO = { "walkable": [0] }

# LEVELS
LEVEL_ARENA = "data/level.txt"

# Movement
DAMPING_FACTOR = 100	# Speed damping factor

# Entities
PLAYER_SPAWN_POINT = (WORLD_WIDTH // 2, WORLD_HEIGHT // 2)
SPAWN_DISTANCE = 2 * TILE_SIZE

ENEMIES = [
	{ "sprite": "geezer_1.png", "max_hp": 40, "base_attack": 5, "base_defense": 10, "speed": 18, "sight_radius": 120 },
	{ "sprite": "geezer_2.png", "max_hp": 60, "base_attack": 15, "base_defense": 15, "speed": 22, "sight_radius": 280 },
	{ "sprite": "barney.png", "max_hp": 80, "base_attack": 25, "base_defense": 25, "speed": 26, "sight_radius": 240 },
]

# Colors
DBG_COLLISION_PLAYER 	= (220, 40, 160)
DBG_COLLISION_ENEMY 	= (180, 240, 60)
DBG_COLLISION_TILES 	= (40, 80, 200)

# Miscellanea
RECT_SIDES = ["top", "bottom", "left", "right"]
