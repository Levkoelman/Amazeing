import shutil

CELL_WIDTH = 6
CELL_HEIGHT = 4


def validate_maze_size(width: int, height: int) -> bool:
    """Check whether the requested maze size fits in the terminal.

    Calculates the required display dimensions based on the maze size and
    cell dimensions. If the maze does not fit, prints the maximum supported
    maze size for the current terminal and returns False.

    Args:
        width: Width of the maze in cells.
        height: Height of the maze in cells.

    Returns:
        True if the maze fits in the terminal, otherwise False.
    """
    terminal = shutil.get_terminal_size()

    required_width = width * CELL_WIDTH + 1
    required_height = height * CELL_HEIGHT + 1

    available_width = terminal.columns
    available_height = terminal.lines - 6

    if (
        required_width > available_width or
        required_height > available_height
    ):

        max_width = max(0, (available_width - 1) // CELL_WIDTH)
        max_height = max(0, (available_height - 1) // CELL_HEIGHT)

        print(
            "Maze does not fit the terminal. "
            f"Maximum maze size for current terminal display: "
            f"{max_width} x {max_height} cells. "
            f"Requested size: {width} x {height} cells. "
        )
        return False
    return True
