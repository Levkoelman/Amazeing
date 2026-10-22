from .maze_generator import directions, is_outside_maze, remove_wall, add_wall
import random


def count_closed_walls(cell: int) -> int:
    """Count how many walls of a cell are closed.

    Args:
        cell: The wall value of a cell. (0 - 15)

    Returns:
        the number of closed walls (0 - 4)
    """
    amount = 0
    for wall in directions:
        if cell & wall:
            amount += 1
    return amount


def find_dead_ends(maze: list[list[int]]) -> list[tuple[int, int]]:
    """find all dead ends in the maze, i.e. cells with exacly
    three closed walls.

    Cells with all four walls closed (the "42" pattern) are not included.

    Args:
        maze: The maze grid, indexed as maze [y][x].

    Returns:
        The (x, y) coordinates of every dead-end cell.
    """
    dead_ends: list[tuple[int, int]] = []
    for y, row in enumerate(maze):
        for x, cell in enumerate(row):
            if count_closed_walls(cell) == 3:
                dead_ends.append((x, y))
    return dead_ends


def get_removable_walls(
    maze: list[list[int]],
    cell: tuple[int, int],
    pattern_cells: set[tuple[int, int]]
) -> list[int]:
    """Get a list of all the walls that can be removed from a cell.

    A wall counts as removable when it is closed, does not lie on the
    outer border of the maze, and does not lead into a cell of the
    '42' pattern.

    Args:
        maze: The maze grid, indexed as maze[y][x].
        cell: The (x, y) poisiton of the cell.
        pattern_cells: The (x, y) positions of the '42' pattern cells.

    Returns:
        A list of walls bits(N=1, E=2, S=4, W=8) that cn be removed.
        The list is empty if no wall can be removed.
    """
    removable_walls: list[int] = []
    height = len(maze)
    width = len(maze[0])
    cx, cy = cell
    for wall in directions:
        if not maze[cy][cx] & wall:
            continue
        dirs, _ = directions[wall]
        dx, dy = dirs
        nx = cx + dx
        ny = cy + dy
        if is_outside_maze(nx, ny, width, height):
            continue
        if (nx, ny) in pattern_cells:
            continue
        removable_walls.append(wall)
    return removable_walls


def is_open_block(
    maze: list[list[int]],
    cell: tuple[int, int]
) -> bool:
    """check wether a 3x3 block of cells has no inner walls.

    Only the walls between the nine cells are checked: the east walls
    of the left two columns and the south walls of the top two rows.
    the outer border of the block is ignored.

    Args:
        maze: The maze grid, indexed as maze[y][x].
        cell: the (x, y) position of the top-left cell of the block.

    Returns:
        True if all inner walls are ope, False otherwise.
    """
    bx, by = cell
    for y in range(by, by + 3):
        for x in range(bx, bx + 2):
            if maze[y][x] & 2:
                return False
    for y in range(by, by + 2):
        for x in range(bx, bx + 3):
            if maze[y][x] & 4:
                return False
    return True


def has_open_area(maze: list[list[int]]) -> bool:
    """Checks if the maze has an open 3x3 area.

    Every possible top-left position of a 3x3 block is checked with
    is_open_block. The search stops at the first open block it finds.

    Args:
        maze: The maze grid, indexed as maze[y][x].

    Returns:
        True if at least one open 3x3 area exists, False otherwise.
    """
    height = len(maze)
    width = len(maze[0])
    for y in range(height - 2):
        for x in range(width - 2):
            if is_open_block(maze, (x, y)):
                return True
    return False


def braiding(
    maze: list[list[int]],
    pattern_cells: set[tuple[int, int]]
) -> None:
    """Remove walls at dead ends to create loops in the maze.

    For every dead end (a cell with three closed walls), one random
    removable wall is opened. If that creates an open 3x3 area, the
    wall is put back. the maze is changed in place.

    Args:
        maze: The maze grid, indexed as maze[y][x].
        pattern_cells: The (x, y) positions of the '42' pattern cells,
            which must stay closed.
    """
    dead_ends = find_dead_ends(maze)
    for cell in dead_ends:
        x, y = cell
        if count_closed_walls(maze[y][x]) != 3:
            continue
        removable_walls = get_removable_walls(maze, cell, pattern_cells)
        if removable_walls:
            wall = random.choice(removable_walls)
            remove_wall(maze, cell, wall)
            if has_open_area(maze):
                add_wall(maze, cell, wall)
