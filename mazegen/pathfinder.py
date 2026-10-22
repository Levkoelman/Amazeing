from collections import deque
from .maze_generator import directions

wall_letters: dict[int, str] = {
    1: 'N',
    2: 'E',
    4: 'S',
    8: 'W'
}


def solve_maze(
    maze: list[list[int]],
    entry_cell: tuple[int, int],
    exit_cell: tuple[int, int]
) -> str:
    """Find the shortest path from entry to exit using breadth-first search.

    Cells are explored in order of distance from the entry, so the first
    time the exit is reached is always via the shortest route. Moves are
    only made trough open walls. The path is rebuilt by following the
    recorded steps back from the exit.

    Args:
        maze: The maze grid, indexed as maze[y][x]
        entry_cell: The (x, y) coordinates of the start.
        exit_cell: The (x, y) coordinates of the goal.

    Returns:
        The path as a string of directions, e.g. "EESS, using
        N, E, S and W.
    """
    came_from: dict[
        tuple[int, int],
        tuple[tuple[int, int], int] | None,
        ] = {entry_cell: None}
    queue: deque[tuple[int, int]] = deque([entry_cell])
    while queue:
        current = queue.popleft()
        if current == exit_cell:
            break
        for wall in directions:
            cx, cy = current
            if maze[cy][cx] & wall:
                continue
            dirs, _ = directions[wall]
            dx, dy = dirs
            nx = cx + dx
            ny = cy + dy
            if (nx, ny) in came_from:
                continue
            came_from[(nx, ny)] = (current, wall)
            queue.append((nx, ny))
    step = exit_cell
    letters: list[str] = []
    note = came_from[step]
    while note is not None:
        last_cell, wall = note
        letters.append(wall_letters[wall])
        step = last_cell
        note = came_from[step]
    letters.reverse()
    return ("".join(letters))


def path_converter(
    solved_path: str,
    entry: tuple[int, int],
    exit: tuple[int, int]
) -> list[tuple[int, int]]:
    """Converts a solved path into a list of cell coordinates.

    Starts at the entry cell and follows the directions in the solved path
    to calculate the coordinates of each cell along the route.

    Args:
        solved_path: String containing the movement directions (N, E, S, W).
        entry: Coordinates of the maze's entry cell.
        exit: Coordinates of the maze's exit cell.

    Returns:
        List of (x, y) coordinates representing the path from entry to exit.
    """

    x, y = entry
    coordinates = [(x, y)]

    moves = {
        'N': (0, -1),
        'E': (1, 0),
        'S': (0, 1),
        'W': (-1, 0)
    }
    for direction in solved_path:
        dx, dy = moves[direction]
        x += dx
        y += dy
        coordinates.append((x, y))

    return list(coordinates)
