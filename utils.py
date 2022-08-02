# Utilities

try:
    import sys
    import os
    import pygame
except ImportError as importErr:
    print("Couldn't load module. {}".format(importErr))
    sys.exit(2)

# -------------------------------------------------------------------------------------------------

def load_image(name):
    """ Load image and return image object"""
    fullname = os.path.join('data', name)
    try:
        image = pygame.image.load(fullname)
        if image.get_alpha is None:
            image = image.convert()
        else:
            image = image.convert_alpha()
    except pygame.error as message:
        print('Cannot load image: {}'.format(fullname))
        raise SystemExit(message)
    return image
