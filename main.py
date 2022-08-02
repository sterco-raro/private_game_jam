#
# Private Game Jam
# Theme: Salto nel vuoto
#
# Authors:
#	unarmedpile@gmail.com
#	serviceoftaxi@gmail.com
#


try:
    import sys
    import random
    import math
    import os
    import pygame
    from pygame.locals import *

    from constants import GAME_VERSION

except ImportError as importErr:
    print("Couldn't load module. {}".format(importErr))
    sys.exit(2)


# -------------------------------------------------------------------------------------------------


def main():
	print("\n\nPRIVATE GAME JAM. Version: {}\n".format(GAME_VERSION))


# -------------------------------------------------------------------------------------------------


if __name__ == '__main__':
	main()
