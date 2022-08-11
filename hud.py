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
	from utils import load_image
except ImportError as importErr:
	print("Couldn't load module. {}".format(importErr))
	sys.exit(2)


# -------------------------------------------------------------------------------------------------


class Hud(object):
	"""TODO docstring for Hud"""
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

		# Internal variables
		self._line_height = 3 # in pixels
		self._icon_placeholder 	= pygame.transform.scale(load_image("unknown.png"), (TILE_SIZE/2, TILE_SIZE/2))
		self._icon_max_hp 		= pygame.transform.scale(load_image("heart.png"), (TILE_SIZE/2, TILE_SIZE/2))
		self._icon_attack 		= pygame.transform.scale(load_image("weap_hand_L.png"), (TILE_SIZE/2, TILE_SIZE/2))
		self._icon_defense 		= pygame.transform.scale(load_image("defense_placeholder.png"), (TILE_SIZE/2, TILE_SIZE/2))
		self._icon_speed 		= pygame.transform.scale(load_image("speed_placeholder.png"), (TILE_SIZE/2, TILE_SIZE/2))

		# Create font object
		self.font = pygame.font.SysFont(font_name, hud_size, bold=bold, italic=italic)

	def _render_player_life(self, surface, hp, max_hp):
		"""TODO docstring for Hud._render_player_life()"""
		text = "HP {}/{}".format(hp, max_hp)
		text_surface = self.font.render(text, self.antialias, self.color)
		surface.blit(text_surface, (HUD_MARGIN, HUD_MARGIN))

	def _render_kill_counter(self, surface, kill_count):
		"""TODO docstring for Hud._render_kill_counter()"""
		text = "{} Kills".format(kill_count)
		text_surface = self.font.render(text, self.antialias, self.color)
		text_margin_right = self.font.size(text)[0] + HUD_MARGIN
		surface.blit(text_surface, (VIEWPORT_WIDTH - text_margin_right, HUD_MARGIN))

	def _render_player_stats(self, surface, player):
		"""TODO docstring for Hud._render_player_stats()"""
		# line = icon, base value [+ bonus value]
		# line size x = sprite/2 + base value (3 digit) + bonus value (3 digit)
		# line size y = max between sprite/2 and font vertical size, plus wanted line spacing
		line_1 = None
		line_2 = None
		line_3 = None
		line_4 = None
		line_text_1 = ""
		line_text_2 = ""
		line_text_3 = ""
		line_text_4 = ""
		# Lines number
		num_stats = 4
		# Hud size sums
		values_text_size = self.font.size("00 ")
		line_size = (HUD_MARGIN, max(TILE_SIZE / 2, values_text_size[1]) + self._line_height)
		total_hud_height = num_stats * line_size[1] + HUD_MARGIN

		# Fill formatted strings with base and bonus values
		if player.combat.max_hp > player.combat.base_max_hp:
			line_text_1 = "{} +{}".format(player.combat.base_max_hp, player.combat.max_hp - player.combat.base_max_hp)
		else:
			line_text_1 = "{}".format(player.combat.base_max_hp)

		if player.combat.attack_bonus:
			line_text_2 = "{} +{}".format(player.combat.base_attack, player.combat.attack_bonus)
		else:
			line_text_2 = "{}".format(player.combat.base_attack)

		if player.combat.defense_bonus:
			line_text_3 = "{} +{}".format(player.combat.base_defense, player.combat.defense_bonus)
		else:
			line_text_3 = "{}".format(player.combat.base_defense)

		if player.speed > player.base_speed:
			line_text_4 = "{} +{}".format(player.base_speed, player.speed - player.base_speed)
		else:
			line_text_4 = "{}".format(player.base_speed)

		# Create font surfaces
		line_1 = self.font.render(line_text_1, self.antialias, self.color)
		line_2 = self.font.render(line_text_2, self.antialias, self.color)
		line_3 = self.font.render(line_text_3, self.antialias, self.color)
		line_4 = self.font.render(line_text_4, self.antialias, self.color)

		# Draw surfaces
		surface.blit(self._icon_max_hp, (line_size[0], VIEWPORT_HEIGHT - 4 * line_size[1] - HUD_MARGIN))
		surface.blit(self._icon_attack, (line_size[0], VIEWPORT_HEIGHT - 3 * line_size[1] - HUD_MARGIN))
		surface.blit(self._icon_defense, (line_size[0], VIEWPORT_HEIGHT - 2 * line_size[1] - HUD_MARGIN))
		surface.blit(self._icon_speed, (line_size[0], VIEWPORT_HEIGHT - 1 * line_size[1] - HUD_MARGIN))
		surface.blit(line_1, (TILE_SIZE/2 + line_size[0], VIEWPORT_HEIGHT - 4 * line_size[1] - HUD_MARGIN))
		surface.blit(line_2, (TILE_SIZE/2 + line_size[0], VIEWPORT_HEIGHT - 3 * line_size[1] - HUD_MARGIN))
		surface.blit(line_3, (TILE_SIZE/2 + line_size[0], VIEWPORT_HEIGHT - 2 * line_size[1] - HUD_MARGIN))
		surface.blit(line_4, (TILE_SIZE/2 + line_size[0], VIEWPORT_HEIGHT - 1 * line_size[1] - HUD_MARGIN))

	def render(self, surface, text, x, y, color=None):
		"""TODO docstring for Hud.render()"""
		if not surface: return
		# Render text to font surface
		text_surface = self.font.render(text, self.antialias, color if color else self.color)
		# Draw text on surface
		surface.blit(text_surface, (x, y))

	def render_hud(self, surface, player, kill_count):
		"""TODO docstring for Hud.render_hud()"""
		# Render top left hud: player life
		self._render_player_life(surface, player.combat.hp, player.combat.max_hp)
		# Render top right hud: kill counter
		self._render_kill_counter(surface, kill_count)
		# Render bottom right hud: player stats
		self._render_player_stats(surface, player)

	def notification(self, surface, text, color=None):
		"""TODO docstring for Hud.notification()"""
		pass
