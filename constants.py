# Gamae constants

import pygame

# General
GAME_NAME = "PrivateGameJam Pazzissima"
GAME_VERSION = "0.1"
WINDOW_TITLE = GAME_NAME

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

MAIN_MENU_TEXT = "CIAO QUESTO È UN GIOCO BELLISSIMO (PREMI SPAZIO)"
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
DAMPING_FACTOR = 100	# Movement speed damping factor

# Entities
ENEMIES = [
	{ "sprite": "geezer_1.png", "max_hp": 4, "base_attack": 1, "base_defense": 0, "speed": 18, "sight_radius": 120 },
	{ "sprite": "geezer_2.png", "max_hp": 6, "base_attack": 1, "base_defense": 1, "speed": 22, "sight_radius": 280 },
	{ "sprite": "barney.png", "max_hp": 8, "base_attack": 2, "base_defense": 1, "speed": 26, "sight_radius": 240 },
]

# Colors
DBG_COLLISION_PLAYER 	= (220, 40, 160)
DBG_COLLISION_ENEMY 	= (180, 240, 60)
DBG_COLLISION_TILES 	= (40, 80, 200)
