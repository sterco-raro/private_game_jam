import esper
import pygame
from code.components.ui import UiButton, UiCursor, UiImage, UiItem, UiSurface, UiText
from code.systems.ui import MenuInputHandler, MenuRendering


def load(file_name):
	world = esper.World()

	# Active display reference
	screen = pygame.display.get_surface()
	screen_size = screen.get_size()

	# Font object
	font_size = 64
	font = pygame.font.SysFont(None, font_size)

	# Entities
	cursor = world.create_entity()
	background = world.create_entity()
	logo = world.create_entity()

	# Components
	cursor_comp = UiCursor( file_name="menu_cursor.png" )
	cursor_comp.rect.center = (screen_size[0]/2, screen_size[1]/2)
	world.add_component( cursor, cursor_comp )

	world.add_component( background, UiSurface( color=(32, 64, 218), size=screen_size ) )

	center_x = screen_size[0]/2
	center_y = screen_size[1]/2

	text = "Scene 2"
	text_surface = font.render(text, True, (255, 255, 255))
	text_rect = text_surface.get_rect( center = (center_x, center_y) )

	image_size = (text_rect.w + 128, text_rect.h + 128)

	image = UiImage( file_name="menu_background.png", size=image_size )
	image.rect.center = ( center_x, center_y )

	world.add_component( logo, image )
	world.add_component( logo, UiText( text=text, surface=text_surface, rect=text_rect, size=font_size ) )

	# Systems
	world.add_processor( MenuInputHandler( cursor_entity=cursor, scene_name=file_name ) )
	world.add_processor( MenuRendering( scene_name=file_name ) )

	return world
