import sys
import time
import importlib
import esper
import pygame


# -------------------------------------------------------------------------------------------------


class WorldManager():
	"""Levels manager (esper worlds)"""

	def __init__(self):
		# TODO BUG? We need to set the mouse cursor visibility here otherwise it will be overwritten
		pygame.mouse.set_visible(False)

		self.worlds = {}	 	# Game levels (esper's Worlds)
		self.worlds_keys = []	# Levels names quick reference list
		self.current = ""		# Current active world

		self._WORLD_PACKAGE = "code.worlds" # World modules package

		# Register event handlers
		esper.set_handler("game_new", self.on_game_new)
		esper.set_handler("game_continue", self.on_game_continue)
		esper.set_handler("quit_to_menu", self.on_quit_to_menu)

		# Setup manager instance
		self.reset()

	# TODO add error checking
	def _load_world(self, file_name):
		"""Load an esper.World definition from @file_name"""
		_module = None
		module_name = "{}.{}".format(self._WORLD_PACKAGE, file_name)

		# Directly call module if it has already been loaded
		if module_name in sys.modules:
			_module = sys.modules[module_name]

		# Dynamically load module when absent
		else:
			_module = importlib.import_module( ".{}".format(file_name), package=self._WORLD_PACKAGE )

		# Load world definition
		return _module.load(file_name)

	def on_game_new(self):
		"""Create a new game"""
		self.current = "rendering_demo"
		self.worlds[self.current] = self._load_world(self.current)
		time.sleep(0.2)
		esper.dispatch_event("scene_change", self.current)

	def on_game_continue(self):
		"""Continue an already created game"""
		print("Event: game_continue")
		time.sleep(0.2)

	def on_quit_to_menu(self):
		"""Go back to main menu and quit current game"""
		del self.worlds[self.current]
		self.current = "main_menu"
		time.sleep(0.2)
		esper.dispatch_event("scene_change", self.current)

	def reset(self):
		"""Setup the manager instance"""
		self.worlds = {} # Useful?
		screen = pygame.display.get_surface() 		# Active display reference
		worlds_list = [ "main_menu", "pause_menu" ] # Available worlds at startup. Note: pause_menu is temporary

		# Try to load each definition in the given files
		for file_name in worlds_list:
			world = self._load_world(file_name)
			if world: self.worlds[file_name] = world

		# Quick reference list to all available worlds
		self.worlds_keys = self.worlds.keys()
		# Main menu is the default view
		self.current = "main_menu"
		# Activate default scene
		esper.dispatch_event("scene_change", self.current)

	def set_active(self, name):
		"""Change active world"""
		if name in self.worlds_keys:
			self.current = name
			esper.dispatch_event("scene_change", name)

	def update(self, dt):
		"""Process currently active world"""
		if self.current:
			self.worlds[self.current].process(dt)

	def quit(self):
		"""Destroy loaded worlds"""
		# Deactivate world updates
		self.current = None
		# Remove elements from loaded modules
		for world_name in self.worlds_keys:
			sys.modules.pop("{}.{}".format(self._WORLD_PACKAGE, world_name))
		# Clear worlds data
		self.worlds.clear()
