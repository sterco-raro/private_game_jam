#
# Private Game Jam
# Theme: Salto nel vuoto
#
# Authors:
#	unarmedpile@gmail.com
#	serviceoftaxi@gmail.com
#


# TODO Design Effect() component-system
# TODO Implement entities health
# TODO Implement entities death
# TODO implement player attacks
# TODO Implement basic AI
# TODO implement enemy attacks
# TODO Implement items
# TODO Implement consumables
# TODO Design a basic particle system


try:
	import sys
	import time
	import random
	from dataclasses import dataclass, field

	import esper
	import pygame
	from pygame.locals import *

	from constants import *
	from utils import load_image
	from game_map import Tilemap
	from hud import Hud
	from data_structures import StaticQuadTree, ObjectsQuadTree, ObjQuadTreeItem

except ImportError as importErr:
	print("Couldn't load module. {}".format(importErr))
	sys.exit(2)


# -------------------------------------------------------------------------------------------------


@dataclass(kw_only=True)
class Velocity(object):
	speed: int = 32
	damping_factor: int = DAMPING_FACTOR
	"""
		Rect works with int, Vector2 works with floats.
		This variable is essential to have the same left and right movement speed,
		otherwise going left will be faster by ~0.4 seconds.
		The explanation is that along the way we lose precision, so it's better
		to do all the calculations in floats (vectors) and eventually assign them to ints (rects).
		See https://stackoverflow.com/questions/18321274/pygame-python-left-seems-to-move-faster-than-right-why
	"""
	position: pygame.Vector2 = pygame.Vector2(0, 0)

	def __post_init__(self):
		self.direction = pygame.Vector2(0, 0)


@dataclass(kw_only=True)
class BasicSprite:
	file_name: str = "unknown.png"
	starting_position: tuple = (0, 0)
	flippable: bool = False
	flipped: bool = False
	should_be_flipped: bool = False
	debug_color: tuple = (0, 0, 0)
	# deflate_x: int = 100
	# deflate_y: int = 100

	def __post_init__(self):
		self.image = load_image(self.file_name)
		if self.flipped:
			self.image = pygame.transform.flip(self.image, False, True)
		self.rect = self.image.get_rect()
		self.rect.center = self.starting_position
		# Deflated rect used for collision detection (one-time .inflate(), much better performances)
		self.hitbox = self.rect.inflate(- TILE_SIZE/2, - TILE_SIZE/2)

		# # Deflate sprite rectangle for better collisions
		# self._scale_collision_rect(self.deflate_x, self.deflate_y)

	# def _clamp_scaling_factor(self, value):
	# 	"""TODO docstring for _clamp_scaling_factor"""
	# 	if value > -2 and value < 2:
	# 		if value >= 0:
	# 			return 2
	# 		else:
	# 			return -2
	# 	return value

	# def _scale_collision_rect(self, percent_x, percent_y):
	# 	"""TODO docstring for _scale_collision_rect"""
	# 	# Invalid arguments
	# 	if percent_x == 0 or percent_y == 0: return
	# 	# Scaling factors. Avoid values in range (-2, 2) to keep the same center as before (not working??)
	# 	dx = self._clamp_scaling_factor( int( self.rect.w * percent_x/100 ) )
	# 	dy = self._clamp_scaling_factor( int( self.rect.h * percent_y/100 ) )
	# 	# Nullify scaling factors when arguments are 100%
	# 	if percent_x == 100: dx = 0
	# 	if percent_y == 100: dy = 0
	# 	# Scale rectangle size
	# 	self.rect.inflate_ip(dx, dy)


@dataclass
class PlayerController:
	active: bool = True
	entities: list[int] = field(default_factory=list)


@dataclass
class SimpleCamera:
	width: int
	height: int
	target: BasicSprite

	def __post_init__(self):
		self.rect = pygame.Rect(0, 0, self.width, self.height)


@dataclass
class Equippable:
	parent: int
	original_image: pygame.Surface
	offset_x: int = 0
	offset_y: int = 0


@dataclass
class Target:
	current: int = -1


# -------------------------------------------------------------------------------------------------


class RenderSystem(esper.Processor):

	def __init__(self, canvas, background, screen, camera, tilemap):
		super().__init__()
		self.screen = screen

		self.canvas = canvas
		self.background = background

		self.camera = camera
		self.tilemap = tilemap

		self.hud = Hud(self.screen, hud_size=FONT_SIZE_HUD, color=(0, 0, 0))

		# TODO TMP
		self.items = []
		# TODO TMP

	# TODO TMP
	def debug_render_rect(self, rect, color=(255, 0, 0), width=1):
		pygame.draw.rect(surface=self.canvas, color=color, rect=rect, width=width)

	def append_debug_rendering(self, rect):
		self.items.append(rect)
	# TODO TMP

	def flip_sprite(self, sprite):
		if sprite.should_be_flipped and not sprite.flipped:
			sprite.image = pygame.transform.flip(sprite.image, True, False)
			sprite.flipped = True
		elif not sprite.should_be_flipped and sprite.flipped:
			sprite.image = pygame.transform.flip(sprite.image, True, False)
			sprite.flipped = False

	def process(self, dt, debug):
		# Redraw map once when debug state changes
		if debug and not self.tilemap.debug_rendering:
			self.tilemap.debug_rendering = True
			self.tilemap.render(self.background)
		elif not debug:
			self.tilemap.debug_rendering = False
			self.tilemap.render(self.background)
		# Clear the screen with the map (background)
		self.canvas.blit(self.background, (0, 0))
		# Render all sprites to the working canvas

		# TODO Processing the list in reversed order to render the player on top of the other sprites, before we get the spritegroups/layering implemented

		for ent, sprite in reversed(self.world.get_component(BasicSprite)):
			# Skip rendering when the current sprite rect is completely outside the screen viewport rect
			if sprite.rect.clip(self.camera.rect).size == (0, 0): continue
			# Update sprites flip logic when needed
			if sprite.flippable: self.flip_sprite(sprite)
			# Draw sprite
			self.canvas.blit(sprite.image, sprite.rect)
			# Draw debug rectangles
			if debug:
				self.debug_render_rect(sprite.rect, color=sprite.debug_color)
				self.debug_render_rect(sprite.hitbox, color=(255, 0, 255))
				# TODO TMP
				if len(self.items) > 0:
					for item in self.items:
						self.debug_render_rect(item, width=0)
					self.items = []
				# TODO TMP
		# Render the working canvas to the screen
		self.screen.blit(self.canvas, (0, 0), self.camera.rect)
		# Draw HUD
		self.hud.render_hud(None, None, debug)
		# Update the display to show changes
		pygame.display.update()


class InputSystem(esper.Processor):

	def process(self, dt, debug):
		pressed = pygame.key.get_pressed()
		for ent, (vel, ctrl) in self.world.get_components(Velocity, PlayerController):
			# Skip inactive controllers
			if not ctrl.active: continue
			# Movement direction
			vel.direction = pygame.Vector2(0, 0)
			# Get direction based on keys pressed
			if pressed[pygame.K_w] or pressed[pygame.K_UP]: 	vel.direction += ( 0, -1)
			if pressed[pygame.K_a] or pressed[pygame.K_LEFT]: 	vel.direction += (-1,  0)
			if pressed[pygame.K_s] or pressed[pygame.K_DOWN]: 	vel.direction += ( 0,  1)
			if pressed[pygame.K_d] or pressed[pygame.K_RIGHT]: 	vel.direction += ( 1,  0)


class MovementSystem(esper.Processor):

	def __init__(self, min_x, max_x, min_y, max_y):
		super().__init__()
		# Map boundaries
		self.min_x = min_x
		self.max_x = max_x
		self.min_y = min_y
		self.max_y = max_y

	def clamp_vector2_ip(self, vector, half_width, half_height):
		vector.x = min(self.max_x - half_width, max(self.min_x + half_width, vector.x))
		vector.y = min(self.max_y - half_height, max(self.min_y + half_height, vector.y))

	def process(self, dt, debug):
		# Get a reference to the collision system
		collision_system = self.world.get_processor(CollisionSystemV1)
		#
		for ent, (vel, sprite) in self.world.get_components(Velocity, BasicSprite):

			# Normalize vector only when length is not 0, otherwise we'll get an error
			if vel.direction.length() > 0:
				vel.direction.normalize_ip()

			# Update position moving along the current direction vector
			new_position = vel.position + vel.direction * dt * vel.speed/vel.damping_factor

			# Clamp sprite to map
			self.clamp_vector2_ip(new_position, sprite.rect.w/2, sprite.rect.h/2)

			# Skip this iteration when the new position is not valid (map collision)
			new_rect = pygame.Rect(sprite.hitbox)
			new_rect.center = new_position
			if collision_system.collide_with_walls(new_rect): continue
			if collision_system.collide_with_objects(new_rect): continue

			# Update position for velocity and sprite components
			vel.position = new_position
			sprite.rect.center = vel.position
			sprite.hitbox.center = vel.position

			# Update flag to flip sprite when necessary
			sprite.should_be_flipped = vel.direction[0] < 0


class CollisionSystemV1(esper.Processor):

	def __init__(self, player, objects, collision_map):
		self.player = player
		self.objects = objects
		self.collision_map = collision_map
		# Static objects quadtree (map collisions like walls)
		self.map_quadtree = StaticQuadTree(items=self.collision_map, bounding_rect=(0, 0, WORLD_WIDTH, WORLD_HEIGHT))
		# Moving objects quadtree (separated because there will probably be a different implementation here later on)
		self.obj_quadtree = ObjectsQuadTree(items=self.objects)

	def reset_collision_map(self, new_collision_map):
		"""Reset map layer collisions. Creates a new StaticQuadTree"""
		self.collision_map = new_collision_map
		self.map_quadtree = StaticQuadTree(items=self.collision_map, bounding_rect=(0, 0, WORLD_WIDTH, WORLD_HEIGHT))

	def reset_objects(self, new_objects):
		"""TODO docstring"""
		self.objects = new_objects
		self.obj_quadtree = ObjectsQuadTree(items=self.objects)

	def add_objects(self, new_objects):
		"""TODO docstring"""
		# TODO Do we really need to recreate a QuadTree each time? Add something like an "insert" function to QuadTree
		if not self.objects: self.objects = []
		if not new_objects: new_objects = []
		self.reset_objects(self.objects + new_objects)

	def remove_objects(self, objects_ids):
		"""TODO docstring"""
		# Remove objects from current QuadTree
		self.obj_quadtree.delete_objects_list(objects_ids)
		# Collect and delete objects from internal list
		_to_be_deleted = [ item for item in self.objects if item.entity in objects_ids ]
		for item in _to_be_deleted:
			self.objects.remove(item)

	def collide_with_walls(self, rect):
		"""TODO docstring"""
		return len(self.map_quadtree.hit(rect)) != 0

	def collide_with_objects(self, rect):
		"""TODO docstring"""
		return len(self.obj_quadtree.hit(rect)) != 0

	def process(self, dt, debug):
		#
		player_ctrl = self.world.component_for_entity(self.player, PlayerController)
		player_sprite = self.world.component_for_entity(self.player, BasicSprite)
		# TODO We're temporary checking the sprite rect instead of its hitbox to render a collision rect
		hits = self.obj_quadtree.hit(player_sprite.rect)
		if len(hits) != 0:
			for rect in hits:
				self.world.get_processor(RenderSystem).append_debug_rendering(rect)


class CrosshairSystem(esper.Processor):

	def __init__(self, crosshair, camera_target):
		super().__init__()
		self.crosshair = crosshair
		self.camera_target = camera_target

	def process(self, dt, debug):
		# Skip processing when cursor is absent
		if not self.crosshair: return
		# Get cursor and camera instances
		cursor = self.world.component_for_entity(self.crosshair, BasicSprite)
		camera = self.world.component_for_entity(self.camera_target, SimpleCamera)
		# Get current mouse position
		position = pygame.mouse.get_pos()
		# Update cursor position based on camera viewport
		cursor.rect.center = pygame.Vector2(position[0] + camera.rect.x, position[1] + camera.rect.y)


class WeaponSystem(esper.Processor):

	def __init__(self):
		super().__init__()

	def process(self, dt, debug):
		for ent, (sprite, equip, target) in self.world.get_components(BasicSprite, Equippable, Target):
			# Get parent entity sprite
			parent_sprite = self.world.component_for_entity(equip.parent, BasicSprite)
			# Default stance
			if target.current == -1:
				lookdir = pygame.Vector2(-1, 0)
			# Get vector pointing at current target
			else:
				target_sprite = self.world.component_for_entity(target.current, BasicSprite)
				lookdir = pygame.Vector2(target_sprite.rect.x - parent_sprite.rect.x, target_sprite.rect.y - parent_sprite.rect.y)
				lookdir = lookdir.rotate(90)
				# Normalize vector only when length is not 0, otherwise we'll get an error
				if lookdir.length() > 0:
					lookdir.normalize_ip()
			# Get current rotation angle based on lookdir
			rotation_angle = lookdir.angle_to((0, 1))
			# Apply Equippable offset
			sprite.rect.center = (	parent_sprite.rect.center[0] + equip.offset_x,
									parent_sprite.rect.center[1] + equip.offset_y)
			# Rotate sprite
			sprite.image = pygame.transform.rotate(equip.original_image, rotation_angle)


class ViewportSystem(esper.Processor):

	def __init__(self, max_width, max_height):
		super().__init__()
		self.max_width = max_width
		self.max_height = max_height

	def process(self, dt, debug):
		for ent, (cam, sprite) in self.world.get_components(SimpleCamera, BasicSprite):
			# Center screen viewport to camera viewport
			x = cam.target.rect.centerx - cam.width // 2
			y = cam.target.rect.centery - cam.height // 2
			# Clamp values to keep the camera limited to map size
			x = min(self.max_width - cam.width, max(0, x))
			y = min(self.max_height - cam.height, max(0, y))
			# Update camera position
			cam.rect.x = x
			cam.rect.y = y


# -------------------------------------------------------------------------------------------------


def spawn_player(world):
	# Player entity and position vector are needed by other entities init code, so we put them here
	player = world.create_entity()
	player_pos = pygame.Vector2(WORLD_WIDTH//2 - TILE_SIZE//2, WORLD_HEIGHT//2 - TILE_SIZE//2)

	# Mouse cursor entity
	crosshair = world.create_entity()
	world.add_component(crosshair, BasicSprite(file_name="cursor_crosshair.png", debug_color=(0, 0, 0)))

	# Player weapons
	weapon_left = world.create_entity()
	weapon_left_pos = player_pos - (20, 0)
	weapon_left_sprite = BasicSprite(file_name="weap_hand_L.png", starting_position=weapon_left_pos, flipped=True, debug_color=(255, 80, 255))
	world.add_component(weapon_left, Velocity(position=weapon_left_pos))
	world.add_component(weapon_left, weapon_left_sprite)
	world.add_component(weapon_left, Equippable(parent=player, original_image=weapon_left_sprite.image, offset_x=-20))
	world.add_component(weapon_left, Target(current=crosshair))
	weapon_right = world.create_entity()
	weapon_right_pos = player_pos + (20, 0)
	weapon_right_sprite = BasicSprite(file_name="weap_hand_L.png", starting_position=weapon_right_pos, debug_color=(255, 80, 255))
	world.add_component(weapon_right, Velocity(position=weapon_right_pos))
	world.add_component(weapon_right, weapon_right_sprite)
	world.add_component(weapon_right, Equippable(parent=player, original_image=weapon_right_sprite.image, offset_x=20))
	world.add_component(weapon_right, Target(current=crosshair))

	# Player entity
	player_sprite = BasicSprite(file_name="fatso.png", starting_position=player_pos, flippable=True, debug_color=(80, 255, 80))
	camera = SimpleCamera(width=VIEWPORT_WIDTH, height=VIEWPORT_HEIGHT, target=player_sprite)
	world.add_component(player, Velocity(position=player_pos))
	world.add_component(player, player_sprite)
	world.add_component(player, PlayerController(entities=[crosshair, weapon_left, weapon_right]))
	world.add_component(player, camera)
	world.add_component(player, Target(current=crosshair))

	# Return entity ID
	return (player, crosshair, camera)


def spawn_enemies(how_many, player, world):
	entities = []

	# Lower clamp for the number of enemies to spawn
	if how_many < 0: how_many = 0

	# Loop variables
	enemy = None
	enemy_pos = None
	enemy_sprite = None
	enemy_sprite_pos = None
	collisions = []			# QuadTreeItem list
	current_entity_ids = []	# Entities IDs list

	# Create given number of enemy entities
	for i in range(how_many):

		# Create new enemy entity
		enemy = world.create_entity()
		enemy_pos = pygame.Vector2(	random.randint(2 * TILE_SIZE, WORLD_WIDTH - 2 * TILE_SIZE),
									random.randint(2 * TILE_SIZE, WORLD_HEIGHT - 2 * TILE_SIZE))
		enemy_sprite = BasicSprite(	file_name=random.choice(["geezer_1.png", "geezer_2.png", "barney.png"]),
									starting_position=enemy_pos, debug_color=(255, 255, 80))
									# deflate_x=-50, deflate_y=-20)

		# Build entity with components
		world.add_component(enemy, enemy_sprite)
		world.add_component(enemy, Target(current=-1))

		# Store entity ID
		current_entity_ids.append(enemy)
		# Store entity ID and sprite rect for the collision system
		collisions.append(ObjQuadTreeItem(entity=enemy, rect=enemy_sprite.hitbox))

		# # Randomly add left-hand weapon
		# if random.randint(0, 1):
		# 	offset_x = random.randint(18, 22)
		# 	enemy_weapon_left = world.create_entity()
		# 	enemy_weapon_left_pos = enemy_pos - (offset_x, 0)
		# 	enemy_weapon_left_sprite = BasicSprite(file_name="weap_hand_L.png", starting_position=enemy_weapon_left_pos, flipped=True, debug_color=(255, 80, 255))
		# 	world.add_component(enemy_weapon_left, Velocity(position=enemy_weapon_left_pos))
		# 	world.add_component(enemy_weapon_left, enemy_weapon_left_sprite)
		# 	world.add_component(enemy_weapon_left, Equippable(parent=enemy, original_image=enemy_weapon_left_sprite.image, offset_x=offset_x))
		# 	world.add_component(enemy_weapon_left, Target(current=player))
		# 	# Store weapon entity ID
		# 	current_entity_ids.append(enemy_weapon_left)

		# # Randomly add right-hand weapon
		# if random.randint(0, 1):
		# 	offset_x = - random.randint(18, 22)
		# 	enemy_weapon_right = world.create_entity()
		# 	enemy_weapon_right_pos = enemy_pos + (offset_x, 0)
		# 	enemy_weapon_right_sprite = BasicSprite(file_name="weap_hand_L.png", starting_position=enemy_weapon_right_pos, debug_color=(255, 80, 255))
		# 	world.add_component(enemy_weapon_right, Velocity(position=enemy_weapon_right_pos))
		# 	world.add_component(enemy_weapon_right, enemy_weapon_right_sprite)
		# 	world.add_component(enemy_weapon_right, Equippable(parent=enemy, original_image=enemy_weapon_right_sprite.image, offset_x=offset_x))
		# 	world.add_component(enemy_weapon_right, Target(current=player))
		# 	# Store weapon entity ID
		# 	current_entity_ids.append(enemy_weapon_right)

		# Collect current entity complete IDs list
		entities.append(current_entity_ids)
		# Clear temporary IDs
		current_entity_ids = []

	# Update collision system's objects list
	world.get_processor(CollisionSystemV1).add_objects(collisions)

	# Return entities ID list
	return entities


def create_level_arena(viewport):
	"""TODO docstring for create_level_arena"""

	# Window title
	pygame.display.set_caption("POSTE ITALIANE")

	# Drawing surfaces
	canvas = pygame.Surface((WORLD_WIDTH, WORLD_HEIGHT)).convert()
	background = pygame.Surface((WORLD_WIDTH, WORLD_HEIGHT)).convert()

	# Background map
	tilemap = Tilemap(size=(MAP_WIDTH, MAP_HEIGHT), file_name=LEVEL_ARENA)
	tilemap.render(background)

	# ECS container object
	world = esper.World()

	# Create the player entity along with all of its components
	player, crosshair, camera = spawn_player(world)

	# Add systems to world
	world.add_processor(InputSystem())
	world.add_processor(MovementSystem(min_x=0, max_x=WORLD_WIDTH, min_y=0, max_y=WORLD_HEIGHT))
	world.add_processor(CollisionSystemV1(player=player, objects=None, collision_map=tilemap.collision_map))
	world.add_processor(CrosshairSystem(crosshair=crosshair, camera_target=player))
	world.add_processor(WeaponSystem())
	world.add_processor(ViewportSystem(max_width=WORLD_WIDTH, max_height=WORLD_HEIGHT))
	world.add_processor(RenderSystem(canvas=canvas, background=background, screen=viewport, camera=camera, tilemap=tilemap))

	# Create some dummy entities to test collisions
	enemies = spawn_enemies(8, player, world)

	# Return level instance (ECS world)
	return (player, enemies, world)

def notify_builder(world):
	def notify(text):
		world.get_processor(RenderSystem).hud.notify(text)
	return notify


# -------------------------------------------------------------------------------------------------


def run():
	dt = 0 			# Time passed since last tick
	player = 0 		# Player ID
	enemies = []	# Enemies IDs list
	world = None	# World instance

	# Initialize pygame
	pygame.init()
	pygame.mouse.set_visible(False)
	# Screen viewport
	viewport = pygame.display.set_mode(SCREEN_SIZE.size)

	# Create a clock instance (FPS limit)
	clock = pygame.time.Clock()

	# Generate level and get related world instance
	player, enemies, world = create_level_arena(viewport)

	notify = notify_builder(world)
	notify("Oh no! Poste Italiane!!!")

	debug = False		# Enable debugging
	events = None		# Pygame events list
	_to_be_deleted = [] # Temporary utility list
	while 1:
		# Handle pygame events
		events = pygame.event.get()
		for event in events:

			# Window close event
			if event.type == QUIT:
				return

			if event.type == KEYDOWN:
				# Enable debug
				if event.key == K_0:
					debug = not debug
				# Spawn more dummy entities
				if event.key == K_9:
					n = random.randint(8, 16)
					enemies.extend(spawn_enemies(n, player, world))
					notify("Spawned {} entities".format(n))
				# Reset dummy entities
				if event.key == K_8:
					_to_be_deleted = [entity_id for entities in enemies for entity_id in entities]
					length = len(_to_be_deleted)
					# Delete entities from the collision system
					world.get_processor(CollisionSystemV1).remove_objects(_to_be_deleted)
					# Delete entities from the world
					for enemy in _to_be_deleted:
						world.delete_entity(enemy, immediate=True)
					_to_be_deleted = []
					# Spawn new entities
					n = random.randint(8, 16)
					enemies = spawn_enemies(n, player, world)
					notify("-{}, +{} entities".format(length, n))

		# Update systems
		world.process(dt, debug)

		# Limit fps
		dt = clock.tick(60)

	# Clear world entities and components?
	world.clear_database()


# -------------------------------------------------------------------------------------------------


if __name__ == '__main__':
	run()
	pygame.quit()
