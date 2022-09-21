import copy
import random
import esper
import pygame
from code.settings 				import *
from code.systems.animation 	import AnimationController
from code.systems.camera 		import CameraFollowManager
from code.systems.input 		import InputHandler
from code.systems.physics 		import PhysicsSimulation
from code.systems.rendering 	import LayeredRendering
from code.components.camera 	import CameraFollow
from code.components.controller import PlayerController
from code.components.hitbox 	import Hitbox
from code.components.map 		import Tile, TileMap
from code.components.physics 	import PhysicsBody
from code.components.sprite 	import StaticSprite, AnimatedSprite


# -------------------------------------------------------------------------------------------------


def create_world_map(world):

	# Entity
	tilemap = world.create_entity()

	# Components
	tileset = {
		"0": Tile( file_name=SPRITE_WATER, 	layer=RENDERING_LAYERS["water"], 	scale_size=(48, 48), walkable=False ),
		"1": Tile( file_name=SPRITE_FLOOR, 	layer=RENDERING_LAYERS["ground"], 	walkable=True ),
		"2": Tile( file_name=SPRITE_WALL, 	layer=RENDERING_LAYERS["main"], 	walkable=False ),
		"3": Tile( file_name=SPRITE_CLOUD, 	layer=RENDERING_LAYERS["ceiling"], 	scale_size=(48, 48), walkable=True ),
	}
	tilemap_data = TileMap( file_name = "demo",
							layers = [ "water", "ground", "main", "ceiling" ],
							tileset = tileset )

	# Assign components to entity
	world.add_component( tilemap, tilemap_data )

	# Create wall entities for "main" layer
	for i in range(tilemap_data.map_height):
		for j in range(tilemap_data.map_width):

			# Empty cells
			if tilemap_data.level_data["main"][i][j] == "-1": continue

			# Entity
			entity = world.create_entity()

			# Components
			spawn_point = ( j * TILE_SIZE + TILE_SIZE//2, i * TILE_SIZE + TILE_SIZE//2 )
			wall_sprite = StaticSprite( file_name = "wall.png",
										layer = RENDERING_LAYERS["main"],
										spawn_point = spawn_point )
			# Assign components to entity
			world.add_component( entity, wall_sprite )
			world.add_component( entity, Hitbox( reference_rect = wall_sprite.rect ) )

	# World dimensions
	return ( tilemap_data.world_width, tilemap_data.world_height )


def create_player(world, world_width, world_height):

	# Entity
	player = world.create_entity()

	# Components
	player_sprite = AnimatedSprite( folder 			= "dinosaur",
									frames_table 	= copy.deepcopy(ANIM_TABLE_DINOSAUR),
									layer 			= RENDERING_LAYERS["main"],
									scale_size 		= ( 48, 48 ),
									spawn_point 	= ( world_width/2 - 64, world_height/2 - 64 ),
									speed 			= 8 )
	player_body = PhysicsBody( position = pygame.Vector2( player_sprite.spawn_point ) )
	player_hitbox = Hitbox( scale_factor_x = -50, scale_factor_y = -60, reference_rect = player_sprite.rect )

	# Assign components to entity
	world.add_component( player, player_sprite )
	world.add_component( player, player_hitbox )
	world.add_component( player, PlayerController() )
	world.add_component( player, CameraFollow( target=player_sprite ) )
	world.add_component( player, player_body )

	return player


def create_random_npcs(world, world_width, world_height):

	number = random.randint(5, 20)

	for i in range(number):

		# Entity
		entity = world.create_entity()

		# Components
		scale = ( random.randint(48, 256), random.randint(48, 256) )
		spawn = ( random.randint(scale[0], world_width), random.randint(scale[1], world_height) )

		# Randomly choose between an animated sprite (dinosaur) or a static one (old player)
		if random.randint(0, 1):
			entity_sprite = AnimatedSprite(
				duration		= ANIM_DURATION_DINOSAUR,
				folder 			= "dinosaur",
				frames_table 	= copy.deepcopy( ANIM_TABLE_DINOSAUR ),
				layer 			= RENDERING_LAYERS["main"],
				scale_size 		= scale,
				spawn_point 	= spawn,
				speed 			= ANIM_SPEED_DINOSAUR
			)
		else:
			entity_sprite = StaticSprite(
				file_name 	= "fatso.png",
				layer 		= RENDERING_LAYERS["main"],
				scale_size 	= scale,
				spawn_point = spawn
			)

		entity_hitbox = Hitbox(
			offset_y = int(scale[1] / 4),
			scale_factor_x = -50,
			scale_factor_y = -60,
			reference_rect = entity_sprite.rect
		)

		# Assign components to entity
		world.add_component( entity, entity_sprite )
		world.add_component( entity, entity_hitbox )


# -------------------------------------------------------------------------------------------------


def load(file_name):
	world = esper.World()

	# Active display reference
	screen = pygame.display.get_surface()
	screen_size = screen.get_size()

	# Font object
	font_size = 64
	font = pygame.font.SysFont(None, font_size)

	width, height = create_world_map(world)

	player = create_player( world, width, height )

	create_random_npcs( world, width, height )

	# TODO The physics simulation should run before the rendering phase but doing so will result in jitering movement
	# TODO It works fine for now but I don't know if this sorting will result in errors later on

	# Systems
	world.add_processor( InputHandler() )
	world.add_processor( CameraFollowManager( max_width=width, max_height=height, camera_id=player ) )
	world.add_processor( AnimationController() )
	world.add_processor( LayeredRendering( scene_name=file_name, world_width=width, world_height=height ) )
	world.add_processor( PhysicsSimulation( bounding_rect=(0, 0, width, height) ) )

	return world
