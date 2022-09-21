import os
import pygame
from code.settings import GRAPHICS_FOLDER


# -------------------------------------------------------------------------------------------------


def import_folder(path, size):
	"""Load all images in the given @path. Slightly modified version of ClearCode Sproutland tutorial code (yt)"""

	# Loaded images
	surfaces = []

	# Os walk iterator, holds the folder contents and eventual subfolders
	iterator = os.walk( os.path.join( GRAPHICS_FOLDER, path ) )

	# For each subfolder in @path
	for current_path, folders, files in iterator:

		# For each file in the current folder, sorted by name
		for image in sorted(files):

			# Load the current file or load and scale when @size is present
			image_path = os.path.join( path, image )
			if size: 	image_surf = load_scaled_image( image_path, size )
			else: 		image_surf = load_image( image_path )

			surfaces.append(image_surf)

	return surfaces


# -------------------------------------------------------------------------------------------------


def load_image(name):
	"""Load image and return image object"""
	fullname = os.path.join(GRAPHICS_FOLDER, name)
	try:
		image = pygame.image.load(fullname)
		if image.get_alpha is None: image = image.convert()
		else:                       image = image.convert_alpha()
	except pygame.error as message:
		print('Cannot load image: {}'.format(fullname))
		raise SystemExit(message)
	return image


# -------------------------------------------------------------------------------------------------


def load_scaled_image(name, size):
	"""Load image and return scaled image object. Size is a tuple"""
	return pygame.transform.scale(load_image(name), size)
