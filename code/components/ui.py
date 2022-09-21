import pygame

from typing import Callable
from dataclasses import dataclass

from code.utils import load_scaled_image


# -------------------------------------------------------------------------------------------------


@dataclass
class UiButton:
	"""Button background (color or image) with hovering support"""
	file_name: str = None
	active_color: tuple = (40, 220, 40)
	inactive_color: tuple = (0, 0, 0)
	rect: pygame.Rect = None
	image: pygame.Surface = None
	size: tuple = (64, 64)
	hovering: bool = False

	def __post_init__(self):
		if self.file_name:
			self.image = load_scaled_image(self.file_name, self.size)
			self.rect = self.image.get_rect()


# -------------------------------------------------------------------------------------------------


@dataclass
class UiCursor:
	"""Mouse cursor"""
	file_name: str = "unknown.png"
	size: tuple = (48, 48)

	def __post_init__(self):
		self.image = load_scaled_image(self.file_name, self.size)
		self.rect = self.image.get_rect()


# -------------------------------------------------------------------------------------------------


@dataclass
class UiImage:
	"""Image loaded from disk"""
	file_name: str = "unknown.png"
	size: tuple = (64, 64)

	def __post_init__(self):
		self.image = load_scaled_image(self.file_name, self.size)
		self.rect = self.image.get_rect()


# -------------------------------------------------------------------------------------------------


@dataclass
class UiItem:
	"""Logical item with an action"""
	rect: pygame.Rect
	callback: Callable[[None], None]


# -------------------------------------------------------------------------------------------------


@dataclass
class UiSurface:
	"""Basic monochrome pygame.Surface"""
	color: tuple = (255, 255, 255)
	size: tuple = (64, 64)

	def __post_init__(self):
		self.image = pygame.Surface(self.size)
		self.image.fill(self.color)
		self.rect = self.image.get_rect()


# -------------------------------------------------------------------------------------------------


@dataclass
class UiText:
	"""Ui text container"""
	text: str = ""
	surface: pygame.Surface = None
	rect: pygame.Rect = None
	size: int = 32
