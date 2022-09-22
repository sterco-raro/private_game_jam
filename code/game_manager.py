import time
import esper
import pygame
from code.settings import *
from code.world_manager import WorldManager

# -------------------------------------------------------------------------------------------------


class GameManager():
	"""General program manager"""

	def __init__(self):
		# Setup pygame
		pygame.init()

		self.screen 		= None	# Main window surface
		self.clock 			= None 	# FPS limiter
		self.world 			= None	# WorldManager instance

		self.running 		= False	# Game loop state
		self.debug 			= False # Manager debug state
		self.collisions 	= True 	# Collision detection

		self.target_fps 	= FPS_LIMIT
		self.fixed_dt 		= FIXED_DELTA_TIME
		self.screen_flags 	= SCREEN_MODE_FLAGS

		# Register event handlers
		esper.set_handler("quit_to_desktop", self.on_game_quit)

		# Setup manager instance
		self.reset()

	def on_game_quit(self):
		"""Clean exit"""
		self.world.quit()
		self.running = False
		if not PROFILING_FILE.closed:
			PROFILING_FILE.close()
		time.sleep(0.5)

	def show_splash_screen(self):
		"""Quick and dirty splash screen"""

		# A warm, welcoming message
		message = "Pippo Baudo non esiste"
		font = pygame.font.SysFont(None, 64)
		font_size = font.size(message)

		# Centered text coords
		size = self.screen.get_size()
		center_x = size[0]/2 - font_size[0]/2
		center_y = size[1]/2 - font_size[1]/2

		# A greenish background
		background = pygame.Surface(size)
		background.fill((218, 253, 175))
		self.screen.blit(background, (0, 0))

		# A black text
		text_surface = font.render(message, True, (0, 0, 0))
		self.screen.blit(text_surface, (center_x, center_y))

		# Show changes
		pygame.display.update()

	def reset(self):
		"""Instance setup"""

		# Close active windows
		pygame.display.quit()

		# Reset current instance
		self.screen = pygame.display.set_mode( (SCREEN_WIDTH, SCREEN_HEIGHT), self.screen_flags )
		pygame.display.set_caption( WINDOW_TITLE )

		#pygame.event.set_allowed( [ pygame.QUIT, pygame.KEYDOWN, pygame.KEYUP ] )
		self.clock = pygame.time.Clock()

		# Give the user some food for thought
		self.show_splash_screen()

		# Initialize the game scenes
		self.world = WorldManager()

		# Start game loop
		self.running = True

	def handle_events(self, events):
		"""Manage pygame events queue"""

		for ev in events:

			# Quit handling
			if ev.type == pygame.QUIT:
				self.on_game_quit()
				self.running = False
				return

			# Debugging keys
			if ev.type == pygame.KEYDOWN:

				# Reset game manager
				if ev.key == pygame.K_r:
					self.reset()

				# Toggle debug
				if ev.key == pygame.K_k:
					self.debug = not self.debug
					esper.dispatch_event("toggle_debug", self.debug)

				# Toggle collision systems
				if ev.key == pygame.K_c:
					self.collisions = not self.collisions
					esper.dispatch_event("toggle_collisions", self.collisions)

				# Reset world manager
				if ev.key == pygame.K_0:
					self.world.reset()

				# Change current fps
				if ev.key == pygame.K_1:
					self.target_fps = 10
				if ev.key == pygame.K_2:
					self.target_fps = 30
				if ev.key == pygame.K_3:
					self.target_fps = 60
				if ev.key == pygame.K_4:
					self.target_fps = 120
				if ev.key == pygame.K_5:
					self.target_fps = 144

				# Change scenes
				if ev.key == pygame.K_ESCAPE:
					self.world.set_active("main_menu")
				if ev.key == pygame.K_p:
					self.world.set_active("rendering_demo")

	def run(self):
		"""Game loop"""

		while self.running:
			# General event handler
			self.handle_events(pygame.event.get())

			# Update current level
			self.world.update(self.fixed_dt)

			# Display updates
			self.clock.tick(self.target_fps)
			pygame.display.update()
