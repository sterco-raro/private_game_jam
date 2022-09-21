import esper
import pygame
from code.components.ui import UiButton, UiCursor, UiImage, UiItem, UiSurface, UiText


# -------------------------------------------------------------------------------------------------


class MenuInputHandler(esper.Processor):
	"""Handle mouse movement and buttons selection"""

	def __init__(self, cursor_entity, scene_name):
		# World ID
		self.scene_name = scene_name
		self.cursor_entity = cursor_entity

		# Mouse Cursor component
		self.cursor = None
		# MenuRendering system
		self.rendering = None

	def process(self, dt):
		# Get the MenuRendering reference
		if not self.rendering:
			self.rendering = self.world.get_processor(MenuRendering)

		# Get the cursor component
		if not self.cursor:
			self.cursor = self.world.component_for_entity(self.cursor_entity, UiCursor)

		# Get current mouse position
		mouse_pos = pygame.mouse.get_pos()
		# Set the cursor sprite position to follow the mouse position
		self.cursor.rect.center = mouse_pos

		# Process user input like mouse movement and clicks
		collision = None
		mouse_left = None
		for ent, (button, item) in self.world.get_components(UiButton, UiItem):

			collision = item.rect.collidepoint(mouse_pos)
			mouse_left, _, __ = pygame.mouse.get_pressed()

			# Check button state for hovering effect (only on buttons with no image surfaces)
			if (
				not button.image 					and
				(not button.hovering and collision) or
				(button.hovering and not collision)
			):
				button.hovering = not button.hovering 			# Update button state
				# TODO Maybe we should use a more "clear" function like "set_redraw(True)"
				self.rendering.on_scene_change(self.scene_name) # Force current scene re-rendering

			# Check collision and user input to activate callback
			if collision and mouse_left:
				item.callback()


# -------------------------------------------------------------------------------------------------


class MenuRendering(esper.Processor):
	"""Build the menu using a custom layered rendering system"""

	def __init__(self, scene_name):
		# World ID
		self.scene_name = scene_name
		# Get a reference to the active display
		self.screen = pygame.display.get_surface()
		self.surface = pygame.Surface(self.screen.get_size())
		# Flag indicating that we need to render the menu again
		self.redraw_ui = True
		# Register an event handler for when there's been a scene change and we need to render the menu
		esper.set_handler("scene_change", self.on_scene_change)

	def on_scene_change(self, name):
		"""Notify the need to update this menu UI"""
		if name == self.scene_name: self.redraw_ui = True

	def reset(self):
		self.redraw_ui = False

		# Layer 0: plain surfaces (background)
		for ent, surface in self.world.get_component(UiSurface):
			self.surface.blit(surface.image, surface.rect)

		# Layer 1: buttons (images with state management)
		color = None
		for ent, button in self.world.get_component(UiButton):
			if button.image:
				self.surface.blit(button.image, button.rect)
			else:
				color = button.inactive_color if not button.hovering else button.active_color
				pygame.draw.rect(self.surface, color, button.rect)

		# Layer 2: images (logos, icons)
		for ent, image in self.world.get_component(UiImage):
			self.surface.blit(image.image, image.rect)

		# Layer 3: text surfaces (header, buttons text)
		for ent, text in self.world.get_component(UiText):
			self.surface.blit(text.surface, text.rect)

	def process(self, dt):
		# Render the menu
		if self.redraw_ui: self.reset()

		# Clear the screen with the static menu surface
		self.screen.blit(self.surface, (0, 0))

		# Blit dynamic entities
		for ent, cursor in self.world.get_component(UiCursor):
			self.screen.blit(cursor.image, cursor.rect)
