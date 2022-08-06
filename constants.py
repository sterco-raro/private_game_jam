# Gamae constants

import pygame

# General
GAME_VERSION = "0.1"

# Window
VIEWPORT_WIDTH = 640
VIEWPORT_HEIGHT = 480

SCREEN_SIZE = pygame.Rect((0, 0, VIEWPORT_WIDTH, VIEWPORT_HEIGHT))

# HUD
FONT_SIZE_HUD = 48
FONT_SIZE_MENU = 24

# Map
TILE_SIZE = 48

MAP_WIDTH = 16
MAP_HEIGHT = 16

WORLD_WIDTH = MAP_WIDTH * TILE_SIZE
WORLD_HEIGHT = MAP_HEIGHT * TILE_SIZE

TILES_INFO = { "walkable": [0] }

# Camera
CAMERA_SMOOTHNESS = 0.05

# Movement
DAMPING_FACTOR = 100	# Movement speed damping factor

# Entities
ENEMIES = [
	{ "sprite": "geezer_1.png", "max_hp": 4, "base_attack": 1, "base_defense": 0, "speed": 18, "sight_radius": 120 },
	{ "sprite": "geezer_2.png", "max_hp": 6, "base_attack": 1, "base_defense": 1, "speed": 22, "sight_radius": 280 },
	{ "sprite": "barney.png", "max_hp": 8, "base_attack": 2, "base_defense": 1, "speed": 26, "sight_radius": 240 },
]

# Colors
DBG_COLLISION_PLAYER 		= (220, 40, 160)
DBG_COLLISION_ENEMY 		= (180, 240, 60)
DBG_COLLISION_TILES 		= (40, 80, 200)
