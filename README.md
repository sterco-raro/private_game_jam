# Private Game Jam

Boia de

## General

Life's hard, you're angry. Enjoy

## Controls

- movement: WASD
- cursor: mouse
- attack: mouse left button
- reset world state: keyboard r (resets enemies for now)
- debug: show collisions rectangles: keyboard k

## Dev Run

#### Linux

- **activate virtual environment**: python .venv/bin/activate
- **install dependencies**: python -m pip install -r requirements.txt
- **run project**: python main.py

#### Windows

same commands, just change .venv structure to .venv/Scripts/activate (check if wrong?)

## Build

- **all in one executable**: python -m PyInstaller --onefile main.py --name private-game-jam
