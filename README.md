# Private Game Jam

Boia de

## General

Life's hard, you're angry. Enjoy

## Controls

- movement: WASD
- cursor: mouse
- attack with left hand: mouse left button
- attack with right hand: mouse right button

## Dev controls

- r: reset world state
- k: show collisions layer

## Dev Run

#### Linux

- **activate virtual environment**: python .venv/bin/activate
- **install dependencies**: python -m pip install -r requirements.txt
- **run project**: python main.py

#### Windows

same commands, just change .venv structure to .venv/Scripts/activate (check if wrong?)

## Build

- **all in one executable**: python -m PyInstaller --onefile main.py --name private-game-jam
