#!/usr/bin/env python3

import random
from typing import Callable, Optional


directions: dict[int, tuple[tuple[int, int], int]] = {
    1: ((0, -1), 4),
    2: ((1, 0), 8),
    4: ((0, 1), 1),
    8: ((-1, 0), 2)
}

FORTY_TWO_PATTERN: list[str] = [
    "#...###",
    "#.....#",
    "###.###",
    "..#.#..",
    "..#.###"
]


def is_outside_maze(
    x: int,
    y: int,
    width: int,
    height: int
) -> bool:
    """Check whether a position lies outside the maze.

    Args:
        x: The x coordinate (column).
        y: The y coordinate (row).
        width: The width of the maze.
        height: The height of the maze.

    Returns:
        True if (x, y) is outside the maze, False otherwise.
    """
    return x < 0 or x >= width or y < 0 or y >= height


def remove_wall(
    maze: list[list[int]],
    cell: tuple[int, int],
    wall: int
) -> None:
    """Remove a wall on both sides; do nothing
    if the neighbour is outside of maze.

    Args:
        maze: the maze grid, indexes as maze[y][x].
        cell: the (x, y) coordinates of the cell.
        wall: the wall to remove (N=1, E=2, S=4, W=8)
    """
    dirs, opp_wall = directions[wall]
    dx, dy = dirs
    cx, cy = cell
    ny = cy + dy
    nx = cx + dx
    height = len(maze)
    width = len(maze[0])
    if (
        is_outside_maze(cx, cy, width, height)
        or is_outside_maze(nx, ny, width, height)
    ):
        return
    maze[cy][cx] = (maze[cy][cx] & ~wall)
    maze[ny][nx] = (maze[ny][nx] & ~opp_wall)


def add_wall(
    maze: list[list[int]],
    cell: tuple[int, int],
    wall: int
) -> None:
    """Add a wall on both sides.

    Args:
        maze: the maze grid, indexes as maze[y][x].
        cell: the (x, y) coordinates of the cell.
        wall: the wall to add (N=1, E=2, S=4, W=8)
    """
    dirs, opp_wall = directions[wall]
    dx, dy = dirs
    cx, cy = cell
    nx = cx + dx
    ny = cy + dy
    maze[cy][cx] = maze[cy][cx] | wall
    maze[ny][nx] = maze[ny][nx] | opp_wall


def make_grid(width: int, height: int) -> list[list[int]]:
    """Create a grid with cells that are all set to 15 (all walls closed).

    Args:
        width: Number of colums in the maze.
        height: Number of rows in the maze
    """
    grid: list[list[int]] = []
    for _ in range(height):
        row = [15] * width
        grid.append(row)
    return grid


def make_visited(width: int, height: int) -> list[list[bool]]:
    """Create a grid that tracks which cells have been visited.

    Args:
        width: Number of colums in the maze.
        height: Number of rows in the maze
    """
    grid: list[list[bool]] = []
    for _ in range(height):
        row = [False] * width
        grid.append(row)
    return grid


def check_neighbors(
    visited_grid: list[list[bool]],
    cell: tuple[int, int]
) -> list[tuple[int, tuple[int, int]]]:
    """Checks if the neighbor of a cell is within the maze and
    if it has been visited

    Args:
        visitited_grid: The grid created by make_visited that tracks
        which cells have been visited cell: The current cell that we
        want to check
    """
    result: list[tuple[int, tuple[int, int]]] = []
    for wall in directions:
        dirs, _ = directions[wall]
        dx, dy = dirs
        cx, cy = cell
        nx = cx + dx
        ny = cy + dy
        height = len(visited_grid)
        width = len(visited_grid[0])
        if is_outside_maze(nx, ny, width, height):
            continue
        if visited_grid[ny][nx]:
            continue
        result.append((wall, (nx, ny)))
    return result


def create_maze(
    grid: list[list[int]],
    visited_grid: list[list[bool]],
    starting_cell: tuple[int, int],
    on_step: Optional[Callable[[], None]] = None,
) -> None:
    """Creates the maze by using the recursive backtracker algorithm.

    Starting from starting_cell, walls are removed between the current
    cell and a random unvisited neighbour until every reachable cell
    has been visited. Cells already marked as visited beforehand (for
    example the "42" pattern) are left untouched.
    Args:
        grid: The maze grid, indexed as grid[y][x]. Modified in place.
        visited_grid: Grid of visited flags, indexed als visited[y][x].
            Modified in place.
        starting_cell: The (x, y) coordinates where carving begins.
    """
    x, y = starting_cell
    visited_grid[y][x] = True
    stack = [starting_cell]
    while stack:
        current = stack[-1]
        neighbours = check_neighbors(visited_grid, current)
        if neighbours:
            chosen = random.choice(neighbours)
            wall, coordinates = chosen
            nx, ny = coordinates
            remove_wall(grid, current, wall)
            visited_grid[ny][nx] = True
            stack.append(coordinates)

            if on_step is not None:
                on_step()
        else:
            stack.pop()


def create_42(
    visited_grid: list[list[bool]],
    entry_cell: tuple[int, int],
    exit_cell: tuple[int, int]
) -> set[tuple[int, int]]:
    """Mark the cells of the "42 pattern as visited, centered in the maze.

    The pattern is skipped if the maze is too small of if the entry or
    exit would fall inside it.

    Args:
        visited_grid: Grid of visited flags, indexed as visisted_grid[y][x].
            Modified in place.
        entry: The (x, y) coordinates of the entry.
        exit: The (x, y) coordinates of the exit.

    Returns:
        The (x, y) cells of the pattern, or an empty set if it was skipped.
    """
    pattern_width = len(FORTY_TWO_PATTERN[0])
    pattern_height = len(FORTY_TWO_PATTERN)
    maze_width = len(visited_grid[0])
    maze_height = len(visited_grid)
    pattern_cells: set[tuple[int, int]] = set()
    if maze_width < (pattern_width + 2) or maze_height < (pattern_height + 2):
        return set()
    x = maze_width // 2 - pattern_width // 2
    y = maze_height // 2 - pattern_height // 2
    for i, row in enumerate(FORTY_TWO_PATTERN):
        for e, character in enumerate(row):
            if character == ".":
                continue
            cx = x + e
            cy = y + i
            pattern_cells.add((cx, cy))
    if entry_cell in pattern_cells or exit_cell in pattern_cells:
        return set()
    for cx, cy in pattern_cells:
        visited_grid[cy][cx] = True
    return pattern_cells
