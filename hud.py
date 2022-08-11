# HUD


# TODO write Hud.notification() and add support for automatic line wrapping


try:
	import sys
	import pygame
	import pygame.font

	from constants import (
		TILE_SIZE,
		HUD_MARGIN,
		VIEWPORT_WIDTH, VIEWPORT_HEIGHT
	)
	from utils import load_scaled_image
except ImportError as importErr:
	print("Couldn't load module. {}".format(importErr))
	sys.exit(2)


# -------------------------------------------------------------------------------------------------


class Hud(object):
	"""UI rendering class
	Returns: object
	Attributes:
		font_name (str)
		size (int)
		bold (bool)
		italic (bool)
		antialias (bool)
		color (rgb tuple)"""
	def __init__(
		self,
		font_name=None, hud_size=32,
		bold=False, italic=False, antialias=True,
		color=(255, 255, 255)
	):
		# Initialize the font module if needed
		if not pygame.font.get_init(): pygame.font.init()
		# Font name, will try a similar alternative or fallback to pygame font
		self.font_name = font_name
		# General text size
		self.size = hud_size
		# Use antialias when rendering text
		self.antialias = antialias
		# Default color to use
		self.color = color
		# Default line height (in pixels)
		self._line_height = 3
		# Default icons size
		self._icons_size = (24, 24)
		# HUD icons by tag
		self._icons = {
			"default": 	load_scaled_image("unknown.png", self._icons_size),
			"life": 	load_scaled_image("heart.png", self._icons_size),
			"damage": 	load_scaled_image("weap_hand_L.png", self._icons_size),
			"shield": 	load_scaled_image("defense_placeholder.png", self._icons_size),
			"movement": load_scaled_image("speed_placeholder.png", self._icons_size),
		}
		# Create font object
		self.font = pygame.font.SysFont(font_name, hud_size, bold=bold, italic=italic)

	def _render_player_life(self, surface, value, max_value):
		"""Internal, renders the top-left section of the HUD: player life"""
		text = "HP {}/{}".format(value, max_value)
		text_surface = self.font.render(text, self.antialias, self.color)
		surface.blit(text_surface, (HUD_MARGIN, HUD_MARGIN))

	def _render_kill_counter(self, surface, kill_count):
		"""Internal, renders the top-right section of the HUD: kill counter (score)"""
		text = "{} Kills".format(kill_count)
		text_surface = self.font.render(text, self.antialias, self.color)
		text_margin_right = self.font.size(text)[0] + HUD_MARGIN
		surface.blit(text_surface, (VIEWPORT_WIDTH - text_margin_right, HUD_MARGIN))

	def _render_player_stats(self, surface, stats):
		"""Internal, renders the bottom-left section of the HUD: player stats and bonuses"""
		# Loop containers
		text = ""
		icon = None
		line = None
		# Number of stats that still need to be rendered
		remaining_lines = len(stats.keys())
		# Starting position for each line
		line_pos_x = HUD_MARGIN
		line_pos_y = 0
		# Starting position for text (next to the icon)
		text_pos_x = self._icons_size[0] + line_pos_x
		# Line size on the y axis (line max height + spacing height)
		line_size_y = max(self._icons_size[1], self.font.size("00 ")[1]) + self._line_height
		# Render stats in lines, in the bottom left section of the HUD
		for key in stats.keys():
			# Build formatted string for current line
			text = "{}".format(stats[key]["base"])
			# Add bonus where needed
			if stats[key]["bonus"] != 0:
				text = "{} +{}".format(text, stats[key]["bonus"])
			# Create font surface
			line = self.font.render(text, self.antialias, self.color)
			# Assign icon by category
			icon = self._icons[key] if key in self._icons else self._icons["default"]
			# Update vertical position
			line_pos_y = VIEWPORT_HEIGHT - remaining_lines * line_size_y - HUD_MARGIN
			# Render icon + text
			surface.blit(icon, (line_pos_x, line_pos_y))
			surface.blit(line,(text_pos_x, line_pos_y))
			# Update line counter
			remaining_lines -= 1

	def render(self, surface, text, x, y, color=None):
		"""Generic rendering method: draws a text at the given coordinates"""
		if not surface: return
		# Render text to font surface
		text_surface = self.font.render(text, self.antialias, color if color else self.color)
		# Draw text on surface
		surface.blit(text_surface, (x, y))

	def render_hud(self, surface, player_stats, kill_count):
		"""Renders the whole game HUD: life, score and player stats"""
		# Top Left
		self._render_player_life(	surface,
									player_stats["life"]["current"],								# HP
									player_stats["life"]["base"] + player_stats["life"]["bonus"]) 	# Max HP
		# Top Right
		self._render_kill_counter(surface, kill_count)
		# Bottom Right
		self._render_player_stats(surface, player_stats)

	def notification(self, surface, text, color=None):
		"""TODO docstring for Hud.notification()"""
		pass
