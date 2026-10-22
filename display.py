def visualize(
    maze: list[list[int]],
    start: tuple[int, int],
    end: tuple[int, int],
    solution: list[tuple[int, int]],
    pattern: set[tuple[int, int]],
    colors: dict[str, str],
    show_path: bool,
) -> None:

    """Display the maze in the terminal using walls, colors, and symbols.

    Draws the maze on a character-based canvas, marks the entry and exit,
    highlights the 42 pattern, and optionally displays the solution path.

    Args:
        maze: 2D grid representing the maze and its walls.
        start: Coordinates of the maze's starting cell.
        end: Coordinates of the maze's ending cell.
        solution: Ordered list of cell coordinates forming the solution path.
        pattern: Set of cell coordinates forming the 42 pattern.
        colors: Dictionary containing the ANSI color codes used for display.
        show_path: Whether to display the solution path in the maze.

    Returns:
        None.
    """

    CELL_WIDTH = 6
    CELL_HEIGHT = 4
    WALL = "█"
    PATH = "+"
    LOGO = "0"

    height = len(maze)
    width = len(maze[0])

    canvas_width = width * CELL_WIDTH + 1
    canvas_height = height * CELL_HEIGHT + 1

    canvas = [
        [" " for _ in range(canvas_width)]
        for _ in range(canvas_height)
    ]

    logo_set = set(pattern)
    logo_walls = set()

    for x, y in logo_set:
        ox = x * CELL_WIDTH
        oy = y * CELL_HEIGHT

        if (x + 1, y) in logo_set:
            for dy in range(1, CELL_HEIGHT):
                logo_walls.add((oy + dy, ox + CELL_WIDTH))

        if (x, y + 1) in logo_set:
            for dx in range(1, CELL_WIDTH):
                logo_walls.add((oy + CELL_HEIGHT, ox + dx))

    for y, maze_row in enumerate(maze):
        for x, cell in enumerate(maze_row):
            ox = x * CELL_WIDTH
            oy = y * CELL_HEIGHT

            if cell & 1:
                for dx in range(CELL_WIDTH + 1):
                    canvas[oy][ox + dx] = WALL

            if cell & 2:
                for dy in range(CELL_HEIGHT + 1):
                    canvas[oy + dy][ox + CELL_WIDTH] = WALL

            if cell & 4:
                for dx in range(CELL_WIDTH + 1):
                    canvas[oy + CELL_HEIGHT][ox + dx] = WALL

            if cell & 8:
                for dy in range(CELL_HEIGHT + 1):
                    canvas[oy + dy][ox] = WALL

    if show_path:
        for (x1, y1), (x2, y2) in zip(solution, solution[1:]):
            px1 = x1 * CELL_WIDTH + CELL_WIDTH // 2
            py1 = y1 * CELL_HEIGHT + CELL_HEIGHT // 2

            px2 = x2 * CELL_WIDTH + CELL_WIDTH // 2
            py2 = y2 * CELL_HEIGHT + CELL_HEIGHT // 2

            if y1 == y2:
                for px in range(min(px1, px2), max(px1, px2) + 1):
                    canvas[py1][px] = PATH
            elif x1 == x2:
                for py in range(min(py1, py2), max(py1, py2) + 1):
                    canvas[py][px1] = PATH

    for y in range(height):
        for x in range(width):
            ox = x * CELL_WIDTH
            oy = y * CELL_HEIGHT

            if (x, y) == start:
                content = "S"
            elif (x, y) == end:
                content = "E"
            elif (x, y) in solution:
                content = PATH
            elif (x, y) in pattern:
                content = LOGO
            else:
                content = " "

            if (x, y) in pattern:
                for dy in range(1, CELL_HEIGHT):
                    for dx in range(1, CELL_WIDTH):
                        canvas[oy + dy][ox + dx] = LOGO
            else:
                px = ox + CELL_WIDTH // 2
                py = oy + CELL_HEIGHT // 2
                canvas[py][px] = content

    for y, canvas_row in enumerate(canvas):
        line = ""

        for x, char in enumerate(canvas_row):
            if char == WALL:
                if (y, x) in logo_walls:
                    line += f"{colors['logo']} {colors['reset']}"
                else:
                    line += f"{colors['wall']}{WALL}{colors['reset']}"

            elif char == PATH:
                if show_path:
                    line += f"{colors['path']} {colors['reset']}"
                else:
                    line += f"{colors['space']} {colors['reset']}"

            elif char == 'S':
                line += f"{colors['entry']}S{colors['reset']}"

            elif char == 'E':
                line += f"{colors['exit']}E{colors['reset']}"

            elif char == LOGO:
                line += f"{colors['logo']} {colors['reset']}"

            else:
                line += char

        print(line)
