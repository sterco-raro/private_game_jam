# Utilities


try:
    import sys
    import os
    import pygame

    from constants import RESOURCES_FOLDER, WORLD_WIDTH, WORLD_HEIGHT
except ImportError as importErr:
    print("Couldn't load module. {}".format(importErr))
    sys.exit(2)


# -------------------------------------------------------------------------------------------------


def load_image(name):
    """Load image and return image object"""
    fullname = os.path.join(RESOURCES_FOLDER, name)
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


# -------------------------------------------------------------------------------------------------


def load_scaled_image(name, size):
    """Load image and return scaled image object. Size is a tuple"""
    return pygame.transform.scale(load_image(name), size)


# -------------------------------------------------------------------------------------------------


def clamp_to_map(position, sprite_w, sprite_h):
    """Clamp a sprite position vector to world map area, returning the clamped vector"""
    x = min(WORLD_WIDTH - sprite_w/2, max(0, position.x))
    y = min(WORLD_HEIGHT - sprite_h/2, max(0, position.y))
    return pygame.Vector2(x, y)
