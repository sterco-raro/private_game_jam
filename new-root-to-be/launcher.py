#
# Codename: Hidden Wheelchair Attack
#
# Authors:
#	unarmedpile@gmail.com
#	serviceoftaxi@gmail.com
#


print("\nUNDER CONSTRUCTION\n")


try:
	import sys
	import pygame
	from code.game_manager import GameManager
except ImportError as importErr:
	print("Cannot load module. {}".format(importErr))
	sys.exit(2)


# -------------------------------------------------------------------------------------------------


if __name__ == '__main__':
	GameManager().run()
	sys.exit(0)
