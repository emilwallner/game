# Game of Life 2 Player

### Game of life core rules
- Any live cell with fewer than two live neighbors dies, as if by under population.
- Any live cell with two or three live neighbors lives on to the next generation.
- Any live cell with more than three live neighbors dies, as if by overpopulation.
- Any dead cell with exactly three live neighbors becomes a live cell, as if by reproduction.

### Game of life 2 Player rules
- The game board is 512 x 512
- Each player gets a 64x64 grid to develop their program 
- The player that has the most surrounding cells, owns the new cell that is born
- Killing cells follows them Game of life core rules
- The player with most live cells after 1000 cycles wins

## Requirements
- python 3.6.5 (is guaranteed to work)
- numpy
- numba
- pyqt5 (for the graphical interface)

`pip install numpy numba pyqt5`

## Usage
The GOLAI package contains all the modules we made.
Let's say you want to use the gameViewer module:
- make sure the "GOLAI" folder is somewhere in your path, you can add it at runtime adding the following code in your script
```python
import sys
sys.path.append("<path/to/GOLAI/parent/folder>")
```
- import the module you need
```python
import GOLAI.gameView as gw
#otherwise
from GOLAI import gameView as gw
```

### Running the interface
The user interface can be started as a module or on it's own.
With both approaches you can preload player files when the application starts.

Inside a script you will need to import the module gameView as previously shown,
then you can call the module's `start()` function.
Using this approach allows the interface to be started with an existing Arena.

The other way to run the interface is from shell, by using the command
`python -m GOLAI.gameView [file1[,file2]]`
