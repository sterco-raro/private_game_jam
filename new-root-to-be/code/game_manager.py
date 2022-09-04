import pygame
# monotonic() instead of time() because the latter is based on system time
from time import monotonic as get_time
from code.settings import *
from code.world_manager import WorldManager

# -------------------------------------------------------------------------------------------------


class GameManager():
	"""TODO docstring for GameManager"""
	def __init__(self):
		# Setup pygame
		if not pygame.get_init(): pygame.init()

		self.screen = None 			# Main window surface
		self.clock = None 			# FPS limiter
		self.pygame_events = None 	# General window events
		self.world = None			# WorldManager instance

		self.reset()

	def reset(self):
		"""Reset this game instance"""
		# Close active windows
		pygame.display.quit()
		# Reset current instance
		self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
		pygame.display.set_caption(WINDOW_TITLE)
		self.clock = pygame.time.Clock()
		self.world = WorldManager()

	def run(self):
		"""Game loop"""
		dt = 0
		current_time = 0
		previous_time = get_time()

		while 1:
			# Deltatime update
			current_time = get_time()
			dt = current_time - previous_time
			previous_time = get_time()

			# General event handler
			self.pygame_events = pygame.event.get()
			for ev in self.pygame_events:
				if ev.type == pygame.QUIT:
					pygame.quit()
					return

			# Display updates
			self.clock.tick(FPS_LIMIT)
			pygame.display.update()
