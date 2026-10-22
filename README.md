*This project has been created as part of the 42 curriculum by fluthra, lekoelma.*

# Description

A-Maze-ing is a maze generator written in Python. From a simple configuration file it generates a random rectangular maze, finds the shortest path from the entry to the exit, writes the result to an output file and shows the maze in the terminal.

## Main features:

- Two generation modes
	PERFECT=True: a perfect maze, with exactly one path between any two cells (no loops).
	PERFECT=False: a Pac-Man-ready board. Every corridor is reachable, the four corners and the centre are open, there are many independent loops, there are no dead ends (bonus) and there is never a fully open 3x3 area.
- A visible "42" pattern, drawn with fully closed cells in the centre of the maze. If the maze is too small, or if the entry/exit overlaps the pattern, the maze is generated without it and a warning is printed.
- Reproducible results: the same SEED always produces the same maze.
- Shortest path from entry to exit, computed with a breadth-first search.
- Output file in the hexadecimal format required by the subject.
- Interactive terminal display (see Visual representation).
- A reusable package, mazegen, that can be installed with pip and used in other projects.

# Instructions

## Requirements

* Python 3.10 or later
* Poetry (install it with pip install poetry)

## Installation
```bash
make install # runs: poetry install
```
This installs the project and its development dependencies (Pydantic, flake8 and mypy) in a virtual environment managed by Poetry.

## Running
```bash
make run
```
Or directly:
```bash
poetry run python3 a_maze_ing.py config.txt
```

## Other Makefile rules
| Rule     | What it does												   |
|----------|---------------------------------------------------------------|
|make debug|Runs the program with Python's debugger (pdb)				   |
|make lint |Runs flake8 . and mypy . with the flags required by the subject|
|make clean|Removes __pycache__, .mypy_cache and dist/                     |

## Building the package
```bash
poetry build
cp dist/mazegen-1.0.0-py3-none-any.whl .
```
The wheel 'mazegen-1.0.0-py3-none-any.whl' is also available at the root of this repository.

# Configuration file

The configuration file contains one KEY=VALUE pair per line.

* Lines starting with # are comments and are ignored. Empty lines are ignored too.
* Keys are case-insensitive (WIDTH and width are the same key).
* Spaces around the key and the value are ignored.
* Each key may appear only once.
* Unknown keys are rejected.

|key        | Required| Format       | Description                                        |
|-----------|---------|--------------|----------------------------------------------------|
|WIDTH      | yes     |integer 2-100 |Number of cells per row                             |
|HEIGHT     | yes     |integer 2-100 |Number of cells per column                          |
|ENTRY      | yes     |x,y           |Entry cell, inside the maze                         |
|EXIT       | yes     |x,y           |Exit cell, inside the maze and different from ENTRY |
|OUTPUT_FILE| yes     |file name     |File the maze is written to                         |
|PERFECT    | yes     |True/False    |Perfect maze or Pac-Man board                       |
|SEED       | no      |integer       |Seed for reproducible mazes (default: random)       |

- With PERFECT=False (Pac-Man mode) the maze must be at least 3x3.
- The maze is only displayed if it fits in the terminal. Otherwise a message is printed, but the maze is still generated and written to OUTPUT_FILE.

## Example (config.txt):
```ini
# Maze size
WIDTH=20
HEIGHT=15

# Entry and exit (x,y), (0,0) is the top-left cell
ENTRY=0,0
EXIT=19,14

OUTPUT_FILE=maze.txt
PERFECT=False
SEED=42
```
If the file cannot be read or contains an invalid value, the program prints a clear message and exits with status 1.

# Output file

Each cell is written as one hexadecimal digit that encodes its closed walls:

|wall |Bit|Value|
|-----|---|-----|
|North|0  |1    |
|East |1  |2    |
|South|2  |4    |
|West |3  |8    |

For example, 9 (1+8) is a cell with its north and west walls closed, and F is a fully closed cell, after the grid there is an empty line, then the entry coordinates, the exit coordinates and the shortest path as a string of N,E,S and W letters.

# Maze generation algorithm

## Generation: recursive backtracker

1. Start with a grid in which every cell has all four walls closed.
2. Mark the cells of the "42" pattern as already visited so the algorithm never enters them and they stay fully closed.
3. Start at the entry cell and push it on a stack.
4. While the stack is not empty: look at the cell on top of the stack. If it has unvisited neighbours, pick one at random, remove the wall between the two cells, mark the neighbour as visited and push it. If it has none, pop the cell (backtrack).

The result is a perfect maze: every cell is reachable and there are no loops.

## Pac-Man mode: braiding

When PERFECT=False, the perfect maze is turned into a board with loops:
1. Find all dead ends (cells with three closed walls).
2. For each dead end, pick a random closed wall that does not lead outside of the maze or into the "42" pattern, and remove it.
3. If removing that wall creates a fully open 3x3 area, the wall is put back.

The only dead ends left are the two cells enclosed by the "42" pattern itself, which the subject allows.

## Why we chose this algorithm
* Simple and easy to explain. The recursive backtracker is one of the most classic maze algorithms, and it only needs a grid, a stack and a "visited" table.
* Always a valid perfect maze. Each cell is visited exactly once and a wall is only removed towards an univisited cell, so the result is always fully connected and has no loops.
* Easy to combine with the "42" pattern. Marking the pattern cells as visited is enough to keep them closed.
* A good base for the Pac_Man mode. Starting from a perfect maze and then braiding the dead ends gives us full control over loops and dead ends.
* BFS for solving always finds the shortest path.

# Reusable Code

The maze generation and solving logic lives in the mazegen package, which has no dependencies outside of the Python standard library. It does not depend on the configuration file or on the display, so it can be reused in other projects.

## Installation
```bash
pip install mazegen-1.0.0-py3-none-any.whl
```

## Usage
```python
from mazegen import MazeGenerator

# width, height, entry (x, y), exit (x, y)
generator = MazeGenerator(20, 15, (0, 0), (19, 14), perfect=False, seed=42)

generator.generate() 	# builds the maze
generator.solve()    	# finds the shortest path

print(generator.maze)			# list[list[int]], indexed maze[y][x]
print(generator.path)			# e.g. "EESWS..."
print(generator.pattern_cells)	# Cells of the "42", empty if it did not fit
```
* Custom parameters: width, height, entry_cell, exit_cell, perfect and seed (default None, which gives a random maze).
* Maze structure: generator.maze is a list of rows. Each cell is an integer from 0 to 15 that encodes its closed walls (N=1, E=2, S=4, W=8).
* Solution: generator.path is the shortest path from entry to exit, as a string of directions (N, E, S, W).
* Calling solve() before generate() raises a RuntimeError.
* The arguments are not validated by the class. In our program, validation is done when the configuration file is loaded (with pydantic).

# Visual Representation

##  Canvas: Sharing walls

* For the visualization of the maze, we first created a canvas. This allows us to control the width and height of each cell, making the maze easier to read in the terminal. The canvas also allows adjacent cells to share walls, meaning that a wall can belong to two neighbouring cells instead of being drawn separately for each cell.

* This approach avoids duplicated walls and ensures that the maze is displayed as a consistent grid. The canvas is built from horizontal and vertical segments, which are drawn according to the walls encoded in each cell.

##  42 pattern

* If there is enough space the maze will contain the "42" pattern in its centre. The pattern is represented by fully closed cells, which are marked as visited before the maze generation algorithm starts. This prevents the algorithm from opening any walls inside the pattern, preserving its shape throughout generation.

* The pattern is displayed using a dedicated colour so that it can be distinguished from the maze walls and corridors. To make sure the walls inside the logo will not be colored similarly to the rest of the maze, an extra set needed to be created. The logo_walls are then added to the set, later to be compared to the walls outside of the logo and colored the same color as the logo cells.

* If the maze is too small to contain the pattern, or if the pattern would overlap with the entry or exit, it is omitted and a warning is printed. This ensures that the pattern does not interfere with the required maze layout.

##  Solution path

* After generating the maze, we use breadth-first search (BFS) to find the shortest path from the entry to the exit. This returns a sequence of directions which is then converted into the corresponding cells. To connect the solution path rather than show a dotted line, the position of the cells on the canvas are compared to each other. Then, from the positions, all the values in between both positions will be colored the same as the path, creating a continuous line.

* The solution path is highlighted with a separate colour, making it easy to follow from the starting point to the destination. The entry and exit are also visually distinguished from the rest of the maze.

##  Color themes and menu

* The terminal visualization supports multiple colour themes: green, blue, red and yellow. Each theme defines colours for the maze walls, entry, exit, solution path and the "42" pattern.

* The user can switch between themes through the interactive menu. The selected theme is applied to the entire maze when it is redrawn.

* The menu also offers the option to show or hide the solution path, re-generate a new maze and exit the program. These options make the terminal display more interactive while keeping the maze generation and solving logic separate from the visualization.

# Team and project management

Team members: Lev Koelman, Francisco Luthra

## Roles of each team member
For this project the roles were divided into two parts:
- **Lev (lekoelma)**:" Configuration parsing and validation (Pydantic), maze generation. the Pac-Man mode (braiding), the shortest path, the output file, the reusable 'mazegen' package
- **Francisco (fluthra)**: The visual representation of the maze in the terminal (canvas with shared walls), the colour themes, drawing the solution path and the "42" pattern, the interactive menu and the animations. 

We agreed early on a shared data format ('list[list[int]]' with one wall bit per direction), so both parts could be developed in parallel.

## Anticipated planning and how it evolved

**Anticipated:** about two weeks of work, three to four days per week. 
- Week 1: the core of the project: configuration, maze generation, solving and the output file and the terminal display
- Week 2: the Pac-Man mode, the reusable package, the Makefile and the documentation.
- The week after: testing, peer review of each other's code.

**How it evolved:**
- The core (configuration, generation, BFS and output) was ready faster than expected.
- The pac-Man mode took more time than planned. The centre of the maze first fell inside the "42" pattern, so we had to change how the pattern is centred, and we added a check that prevents fully open 3x3 areas.
- Building the reusable package was new for us so took a bit longer than expected.
- In the last days we focused on minor improvements and making the animated display.

## What worked well, what can be improved

**What worked well**
- Splitting the work into "logic" and "display" lets us work in parallel without getting in each other's way.
- Agreeing on one data format early made it easy to connect both parts.

**what could be improved**
- We could have agreed earlier on the exact interface between the generator and the display (for example the format of the solution path, which is a string of directions in the package but a list of cells in the display).

# Resources

* The subject provided by the 42 school
* Geeksforgeeks for explanation about new python subjects/functions
* Recursive Backtracking algorithm: https://brilliant.org/wiki/recursive-backtracking/
* Breadth first search: https://www.geeksforgeeks.org/dsa/breadth-first-search-or-bfs-for-a-graph/

## Tools used

* Pydantic: Validation of the config file
* Poetry: dependency management and building the package

## Use of AI

We used an AI assistant (Claude, and ChatGPT) as a tutor. We wrote the code ourselves and used AI to:
- Explain concepts: Wall bits, recursive backtracker, Braiding and packaging
- Review our code: it pointed out bugs and gave hints, which we fixed ourselves.

# License

This project is licensed under the MIT License. See LICENSE.md.