# HUD


try:
	import sys
	import time
	import textwrap
	import pygame
	import pygame.font

	from constants import (
		TILE_SIZE,
		HUD_MARGIN,
		HUD_SPACING,
		HUD_NOTIF_MAX_LINES,
		VIEWPORT_WIDTH, VIEWPORT_HEIGHT
	)
	from utils import load_scaled_image
except ImportError as importErr:
	print("Couldn't load module. {}".format(importErr))
	sys.exit(2)


# -------------------------------------------------------------------------------------------------


class Hud(object):
	"""UI simple rendering class
	Returns: object
	Functions:
		notify
		render_hud
		update
	Attributes:
		font_name (str)
		size (int)
		bold (bool)
		italic (bool)
		antialias (bool)
		color (rgb tuple)"""
	def __init__(
		self,
		surface,
		font_name=None, hud_size=32,
		bold=False, italic=False, antialias=True,
		color=(255, 255, 255)
	):
		# Initialize the font module if needed
		if not pygame.font.get_init(): pygame.font.init()
		# Surface used for rendering
		self.surface = surface
		# Font name, will try a similar alternative or fallback to pygame font
		self.font_name = font_name
		# General text size
		self.size = hud_size
		# Use antialias when rendering text
		self.antialias = antialias
		# Default color to use
		self.color = color
		self.debug_color = (200, 40, 200)
		# Create font object
		self.font = pygame.font.SysFont(font_name, hud_size, bold=bold, italic=italic)
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
		# Static dimensions
		self._char_size = self.font.size("a")													# Single char font sizes (w, h)
		self._stats_line_height = max(self._icons_size[1], self._char_size[1]) + HUD_SPACING 	# Stats section line height
		# Base positions for all the HUD sections (in pixels)
		self.positions = {
			"life": 	(HUD_MARGIN, HUD_MARGIN),
			"score":	(VIEWPORT_WIDTH - HUD_MARGIN, HUD_MARGIN),
			"stats": 	(HUD_MARGIN, VIEWPORT_HEIGHT - HUD_MARGIN),
			"notif":	(4 * HUD_MARGIN + self._icons_size[0] + 4 * self._char_size[0],
						 VIEWPORT_HEIGHT - HUD_MARGIN - self._stats_line_height * HUD_NOTIF_MAX_LINES)
		}
		# Notifications: queue and current elapsed time
		self._history = []
		self._messages_queue = []
		self._last_notification = pygame.time.get_ticks()	# Milliseconds
		# Max characters for each notification line (notification box size / single char size)
		self._notif_max_chars = (VIEWPORT_WIDTH - HUD_MARGIN - self.positions["notif"][0]) // self._char_size[0]

	def _render_debug_border(self, x, y, w, h):
		"""Private, generic rendering method: draws an empty rectangle to act as a simple debug border"""
		pygame.draw.rect(self.surface, self.debug_color, pygame.Rect(x, y, w, h), width=1)

	def _render_text(self, text, x, y, surface=None, color=None):
		"""Private, generic rendering method: draws a text on a surface at the given coordinates"""
		# Use internal surface when none is available in the arguments
		if not surface: surface = self.surface
		# Render text to font surface
		text_surface = self.font.render(text, self.antialias, color if color else self.color)
		# Draw text on surface
		surface.blit(text_surface, (x, y))

	def _render_surface(self, source_surface, x, y, surface=None):
		"""Private, generic rendering method: draws a pygame.Surface on another surface at the given coordinates"""
		# Use internal surface when none is available in the arguments
		if not surface: surface = self.surface
		# Draw text on surface
		surface.blit(source_surface, (x, y))

	def _render_player_life(self, value, max_value, debug):
		"""Private, renders the top-left section of the HUD: player life"""
		text = "HP {}/{}".format(value, max_value)
		self._render_text(text, self.positions["life"][0], self.positions["life"][1])
		# Ugly debug rectangles around this section
		if debug:
			text_size = self.font.size(text)
			self._render_debug_border(	self.positions["life"][0],
										self.positions["life"][1],
										text_size[0],
										text_size[1])

	def _render_kill_counter(self, kill_count, debug):
		"""Private, renders the top-right section of the HUD: kill counter (score)"""
		text = "{} Kills".format(kill_count)
		text_size = self.font.size(text)
		self._render_text(text, self.positions["score"][0] - text_size[0], self.positions["score"][1])
		# Ugly debug rectangles around this section
		if debug:
			self._render_debug_border(	self.positions["score"][0] - text_size[0],
										self.positions["score"][1],
										text_size[0],
										text_size[1])

	def _render_player_stats(self, stats, debug):
		"""Private, renders the bottom-left section of the HUD: player stats and bonuses"""
		# Number of stats that still need to be rendered
		remaining_lines = len(stats.keys())
		# Render stats in lines, in the bottom left section of the HUD
		text = ""
		icon = None
		line_pos_y = 0
		for key in stats.keys():
			# Build formatted string for current line
			text = "{}".format(stats[key]["base"])
			# Add bonus where needed
			if stats[key]["bonus"] != 0:
				text = "{} +{}".format(text, stats[key]["bonus"])
			# Assign icon by category
			icon = self._icons[key] if key in self._icons else self._icons["default"]
			# Update vertical position
			line_pos_y = self.positions["stats"][1] - remaining_lines * self._stats_line_height
			# Render icon + text
			self._render_surface(icon, self.positions["stats"][0], line_pos_y)
			self._render_text(text, self.positions["stats"][0] + self._icons_size[0], line_pos_y)
			# Update line counter
			remaining_lines -= 1
		# Ugly debug rectangles around this section
		if debug:
			self._render_debug_border(	self.positions["stats"][0],
										self.positions["stats"][1] - len(stats.keys()) * self._stats_line_height,
										2 * HUD_MARGIN + self._icons_size[0] + 4 * self._char_size[0],
										len(stats.keys()) * self._stats_line_height)

	def _render_notification(self, text, debug):
		"""Private, renders the bottom-right section of the HUD: notifications"""
		text_len = len(text)
		pos_y = self.positions["notif"][1]
		for i in range(text_len):
			self._render_text(text[i], self.positions["notif"][0], pos_y)
			pos_y += self._stats_line_height
		# Ugly debug rectangles around this section
		if debug:
			self._render_debug_border(	self.positions["notif"][0],
										self.positions["notif"][1],
										VIEWPORT_WIDTH - HUD_MARGIN - self.positions["notif"][0],
										text_len * self._stats_line_height)

	def notify(self, text, cooldown=3):
		"""Add a notification to the system, along with cooldown. Long strings will be splitted into smaller ones"""
		# Ensure cooldown is an int
		try:
			_cooldown = int(cooldown)
		except ValueError as vErr:
			print("Hud.notify(): ValueError: cooldown must be an integer")
			return
		# Wrap text in multiple lines
		lines = textwrap.wrap(text, width=self._notif_max_chars)
		# Split the message into sublists of HUD_NOTIF_MAX_LINES length (if needed)
		chunks = [lines[i:i + HUD_NOTIF_MAX_LINES] for i in range(0, len(lines), HUD_NOTIF_MAX_LINES)]
		# Add each lines group to the notifications queue
		for chunk in chunks:
			# Quick and dirty message object, metadata: cooldown and current time
			message = { "text": chunk, "cooldown": _cooldown * 1000, "datetime": time.localtime() }
			# Store message in notifications queue and history
			self._messages_queue.append(message)
			# Store message in history, with current time
			self._history.append(message)

	def render_hud(self, player_stats, kill_count, debug):
		"""Renders the whole game HUD: life, score and player stats"""
		# Top Left
		self._render_player_life(	player_stats["life"]["current"],								# HP
									player_stats["life"]["base"] + player_stats["life"]["bonus"], 	# Max HP
									debug)
		# Top Right
		self._render_kill_counter(kill_count, debug)
		# Bottom Left
		self._render_player_stats(player_stats, debug)
		# Bottom Right
		self.update(debug)

	def update(self, debug):
		"""Called continuously to update the notifications queue: check cooldown status and display next message"""
		# No messages to handle
		if len(self._messages_queue) == 0:
			# Update timer
			self._last_notification = pygame.time.get_ticks()
			return
		# Check cooldown expiration
		now = pygame.time.get_ticks()
		if now - self._last_notification >= self._messages_queue[0]["cooldown"]:
			# Update timer (needed when the messages queue length is not zero)
			self._last_notification = now
			# Remove current message
			self._messages_queue.pop(0)
		# No messages to handle
		if len(self._messages_queue) == 0: return
		# Render notification on screen, bottom-right section of the HUD
		self._render_notification(self._messages_queue[0]["text"], debug)
