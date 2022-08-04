
import pygame

GAME_VERSION = "0.1"

VIEWPORT_WIDTH = 640
VIEWPORT_HEIGHT = 480

TILE_SIZE = 32

MAP_WIDTH = 24
MAP_HEIGHT = 24

WORLD_WIDTH = MAP_WIDTH * TILE_SIZE
WORLD_HEIGHT = MAP_HEIGHT * TILE_SIZE

SCREEN_SIZE = pygame.Rect((0, 0, VIEWPORT_WIDTH, VIEWPORT_HEIGHT))

CAMERA_SMOOTHNESS = 0.05

# Movement speed damping factor
DAMPING_FACTOR = 100

TILES_INFO = {
	"walkable": [7, 10, 37],
}
