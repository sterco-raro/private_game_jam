import os
import pathlib
import pygame

# General
GAME_NAME 		= "Hidden Wheelchair Attack"
GAME_VERSION 	= "0.1"

FPS_LIMIT 			= 60.0
FIXED_DELTA_TIME 	= 0.01

SCREEN_MODE_FLAGS = pygame.DOUBLEBUF
#SCREEN_MODE_FLAGS = pygame.FULLSCREEN | pygame.DOUBLEBUF

PROFILING_MODE = "w+"
PROFILING_PATH = "profiling.txt"
PROFILING_FILE = open(PROFILING_PATH, PROFILING_MODE)

# Resources
GRAPHICS_FOLDER = os.path.join(pathlib.Path(__file__).parent.resolve().parent, "graphics")

SPRITE_UNKNOWN 	= "unknown.png"
SPRITE_CLOUD 	= "cloud.png"
SPRITE_FLOOR 	= "floor.png"
SPRITE_WALL 	= "wall.png"
SPRITE_WATER 	= "water.png"

# Window
WINDOW_TITLE = GAME_NAME

SCREEN_WIDTH 	= 1280
SCREEN_HEIGHT 	= 720

VIEWPORT_WIDTH 	= SCREEN_WIDTH
VIEWPORT_HEIGHT = SCREEN_HEIGHT

# Map
TILE_SIZE = 48

# Physics
VECTOR_ZERO 			= pygame.Vector2(0, 0)
SPEED_MAX 				= 20.0 		# TODO Test value and change it to the desired max speed
SPEED_BASE 				= 10.0
# TODO Is this still necessary? We used it when the physics simulation code was different (fps-dependant)
SPEED_BASE_FACTOR 		= 1.0 		# Multiplier used to have a small base speed
FRICTION_BASE_FLOOR 	= 0.5 		# 0.5 = almost meaningless, 0.1 = meaningful
ACCELERATION_BASE_FLOOR = 0.5 		# 0.5 = almost meaningless, 0.1 = meaningful

# Colors
STATIC_SPRITE_DEBUG_COLOR 	= (40, 220, 220)
ANIMATED_SPRITE_DEBUG_COLOR = (40, 220, 220)
MAP_TILE_DEBUG_COLOR 		= (220, 220, 40)
HITBOX_DEBUG_COLOR 			= (220, 40, 220)

# Z-axis sorting layers
RENDERING_LAYERS = {
	"void": 	-1,
	"water": 	 0,
	"ground": 	 1,
	"main": 	 2,
	"ceiling": 	 3
}

# Animations
ANIM_SPEED_DINOSAUR 	= 12 	# TODO animation speed unit is ?
ANIM_DURATION_DINOSAUR 	= 0 	# in milliseconds
ANIM_TABLE_DINOSAUR 	= { "idle": [], "moving": [], "hurt": [], "kick": [] }

ANIM_SPEED_EXPLOSION 	= 12 	# TODO animation speed unit is ?
ANIM_DURATION_EXPLOSION = 1500 	# in milliseconds
ANIM_TABLE_EXPLOSION 	= { "big": [] }

# Player actions (in milliseconds)
PLAYER_COOLDOWN_BOMB 	= 1000
PLAYER_DURATION_ATTACK 	= 500
PLAYER_DURATION_HURT 	= 500
