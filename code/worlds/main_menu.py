import esper
import pygame
from code.systems.ui import MenuInputHandler, MenuRendering
from code.components.ui import UiButton, UiCursor, UiImage, UiItem, UiSurface, UiText


def load(file_name):
	world = esper.World()

	# Active display reference
	screen = pygame.display.get_surface()
	screen_size = screen.get_size()

	# Font object
	font_size = 64
	font = pygame.font.SysFont(None, font_size)

	# Miscellanea
	height = 0
	margin = 64
	image = None
	text = ""
	text_size = 0
	text_surface = None
	text_rect = None

	# Entities
	cursor = world.create_entity()
	background = world.create_entity()
	logo = world.create_entity()
	button_1 = world.create_entity()
	button_2 = world.create_entity()
	button_3 = world.create_entity()
	icon_btn_left = world.create_entity()
	icon_btn_right = world.create_entity()

	# Components
	cursor_comp = UiCursor( file_name="menu_cursor.png" )
	cursor_comp.rect.center = (screen_size[0]/2, screen_size[1]/2)
	world.add_component( cursor, cursor_comp )

	world.add_component( background, UiSurface( color=(218, 64, 32), size=screen_size ) )

	text = "Hidden Wheelchair Attack"
	text_surface = font.render(text, True, (255, 255, 255))
	text_rect = text_surface.get_rect( center = (screen_size[0]/2, screen_size[1]/4) )
	image = UiImage( file_name="menu_background.png", size=(text_rect.w + 80, text_rect.h + 80) )
	image.rect.center = ( screen_size[0]/2, screen_size[1]/4 )
	world.add_component( logo, image )
	world.add_component( logo, UiText( text=text, surface=text_surface, rect=text_rect, size=font_size ) )

	text = "New Game"
	text_size = font.size(text)
	height = text_size[1] + 40 + 15
	text_surface = font.render(text, True, (255, 255, 255))
	text_rect = text_surface.get_rect( center = (screen_size[0]/2, screen_size[1]/2 + height) )
	image = UiButton( rect=pygame.Rect( text_rect.x - 20, text_rect.y - 20, text_rect.w + 40, text_rect.h + 40 ) )
	image.rect.center = ( screen_size[0]/2, screen_size[1]/2 + height )
	world.add_component( button_1, image )
	world.add_component( button_1, UiText( text=text, surface=text_surface, rect=text_rect, size=font_size ) )
	world.add_component( button_1, UiItem( rect=image.rect, callback=lambda: esper.dispatch_event("game_new") ) )

	text = "Continue"
	text_size = font.size(text)
	height = (text_size[1] + 40 + 15) * 2
	text_surface = font.render(text, True, (255, 255, 255))
	text_rect = text_surface.get_rect( center = (screen_size[0]/2, screen_size[1]/2 + height) )
	image = UiButton( rect=pygame.Rect( text_rect.x - 20, text_rect.y - 20, text_rect.w + 40, text_rect.h + 40 ) )
	image.rect.center = ( screen_size[0]/2, screen_size[1]/2 + height )
	world.add_component( button_2, image )
	world.add_component( button_2, UiText( text=text, surface=text_surface, rect=text_rect, size=font_size ) )
	world.add_component( button_2, UiItem( rect=image.rect, callback=lambda: esper.dispatch_event("game_continue") ) )

	text = "Exit"
	text_size = font.size(text)
	height = (text_size[1] + 40 + 15) * 3
	text_surface = font.render(text, True, (255, 255, 255))
	text_rect = text_surface.get_rect( center = (screen_size[0]/2, screen_size[1]/2 + height) )
	image = UiButton( rect=pygame.Rect( text_rect.x - 20, text_rect.y - 20, text_rect.w + 40, text_rect.h + 40 ) )
	image.rect.center = ( screen_size[0]/2, screen_size[1]/2 + height )
	world.add_component( button_3, image )
	world.add_component( button_3, UiText( text=text, surface=text_surface, rect=text_rect, size=font_size ) )
	world.add_component( button_3, UiItem( rect=image.rect, callback=lambda: esper.dispatch_event("quit_to_desktop") ) )

	x = margin
	y = screen_size[1] - margin
	image = UiButton( file_name="menu_icon_left.png", size=(128, 128) )
	image.rect.center = ( x, y )
	world.add_component( icon_btn_left, image )
	world.add_component( icon_btn_left, UiItem( rect=image.rect, callback=lambda: print("Left icon callback") ) )

	x = screen_size[0] - margin
	image = UiButton( file_name="menu_icon_right.png", size=(128, 128) )
	image.rect.center = ( x, y )
	world.add_component( icon_btn_right, image )
	world.add_component( icon_btn_right, UiItem( rect=image.rect, callback=lambda: print("Right icon callback") ) )

	# Systems
	world.add_processor( MenuInputHandler( cursor_entity=cursor, scene_name=file_name ) )
	world.add_processor( MenuRendering( scene_name=file_name ) )

	return world
