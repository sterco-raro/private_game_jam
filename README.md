# Codename: Hidden Wheelchair Attack

"Boia de" for historical reasons

## Controls

### Player

- wasd: movement
- b: 	explosive farting
- n: 	drop a bomb
- m: 	kick them in the face
- h:	hurt your own feelings

### Debug

- k: toggle debug
- c: toggle collisions

- r: reset game manager
- 0: reset world manager

- escape: 	change scene to main_menu
- p: 		change scene to rendering_demo

- 1: set fps to 10
- 2: set fps to 30
- 3: set fps to 60
- 4: set fps to 120
- 5: set fps to 144

## Docs

### Run

#### Linux

- **activate virtual environment**: python .venv/bin/activate
- **install dependencies**: python -m pip install -r requirements.txt
- **run project**: python launcher.py

#### Windows

same commands but virtualenv folder structure is different (.venv/Scripts/something?)

### Build

- **all in one executable**: python -m PyInstaller --onefile launcher.py --name HWA

### Project structure

- code
	- components:
	- systems:
	- worlds:
- data
- graphics

### Custom events

- toggle_debug:
- toggle_collisions:
- scene_change:
- game_new:
- game_continue:
- quit_to_menu:
- quit_to_desktop:
