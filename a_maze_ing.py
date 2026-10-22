#!/usr/bin/env python3

import sys
from read_config import load_config, ConfigError, MazeConfig
from mazegen import MazeGenerator
from display import visualize
from write_output import write_output
from mazegen import pathfinder
from colors import COLOR_THEMES
import time
from terminal_size import validate_maze_size


def show_menu(
    maze: list[list[int]],
    entry: tuple[int, int],
    exit: tuple[int, int],
    solution: list[tuple[int, int]],
    pattern: set[tuple[int, int]],
    config: MazeConfig
) -> None:
    """Display an interactive menu for the maze.

    Allows the user to regenerate the maze, show or hide the shortest path,
    change the color theme, or exit the program.

    Args:
        maze: 2D grid representing the maze and its walls.
        entry: Coordinates of the maze's starting cell.
        exit: Coordinates of the maze's ending cell.
        solution: Ordered list of cell coordinates forming the shortest path.
        pattern: Set of cell coordinates forming the 42 pattern.
        config: Configuration object containing the maze settings.

    Returns:
        None.
    """
    theme = "green"
    show_path = True
    already_drawn = True

    while True:
        colors = COLOR_THEMES[theme]
        if not already_drawn:
            print("\033[2J\033[H", end="")
            sys.stdout.flush()

            visualize(
                maze,
                entry,
                exit,
                solution,
                pattern,
                colors,
                show_path,
            )
        already_drawn = False

        print("\n=== MAZE MENU ===")
        print("1. Re-generate a new maze")
        print("2. Show / hide the shortest path")
        print("3. Rotate colors")
        print("0. Exit")

        choice = input("Input choice: ").strip()

        if choice == "1":
            generator = generate(config, animate=True)
            maze = generator.maze
            pattern = generator.pattern_cells
            solution = pathfinder.path_converter(
                generator.path,
                config.entry,
                config.exit)

            animate_path(
                maze,
                entry,
                exit,
                solution,
                pattern,
                COLOR_THEMES[theme])
            already_drawn = True

        elif choice == "2":
            show_path = not show_path

            if show_path:
                animate_path(
                    maze,
                    entry,
                    exit,
                    solution,
                    pattern,
                    colors)
                already_drawn = True

        elif choice == "3":
            if theme == "green":
                theme = "blue"
            elif theme == "blue":
                theme = "red"
            elif theme == "red":
                theme = "yellow"
            elif theme == "yellow":
                theme = "green"

        elif choice == "0":
            break

        else:
            print("Invalid input")
            input("Press Enter to continue")


def animate_path(
    maze: list[list[int]],
    entry: tuple[int, int],
    exit: tuple[int, int],
    solution: list[tuple[int, int]],
    pattern: set[tuple[int, int]],
    colors: dict[str, str],
) -> None:
    """Animate the shortest path from entry to exit in the terminal.

    Args:
        maze: 2D grid representing the maze and its walls.
        entry: Coordinates of the maze's starting cell.
        exit: Coordinates of the maze's ending cell.
        solution: Ordered list of cell coordinates forming the shortest path.
        pattern: Set of cell coordinates forming the 42 pattern.
        colors: Dictionary containing the ANSI color codes used for display.

    Returns:
        None.
    """
    if not solution:
        return

    print("\033[2J\033[H", end="")
    sys.stdout.flush()

    for i in range(1, len(solution) + 1):
        print("\033[H", end="")
        visualize(
            maze,
            entry,
            exit,
            solution[:i],
            pattern,
            colors,
            True,
        )

        sys.stdout.flush()
        time.sleep(0.05)


def generate(
    config: MazeConfig,
    animate: bool = False,
) -> MazeGenerator:
    """Generate and solve a maze, then write it to the output file.

    Creates a MazeGenerator from the configuration, builds the maze
    and find the shortest path. prints a warning if the '42' pattern
    could not be placed. the result is written to config.output_file.

    Args:
        config: The validated maze configuration.

    Returns:
        The MazeGenerator hodlding the maze, the path and the pattern
        cells.
    """
    generator = MazeGenerator(
        config.width,
        config.height,
        config.entry,
        config.exit,
        config.perfect,
        config.seed)

    if animate:
        colors = COLOR_THEMES["green"]
        frame_count = 0

        def on_step(
            maze: list[list[int]],
            pattern: set[tuple[int, int]]
        ) -> None:
            nonlocal frame_count
            frame_count += 1

            if frame_count % 3 != 0:
                return

            print("\033[H", end="")
            visualize(
                maze,
                config.entry,
                config.exit,
                [],
                pattern,
                colors,
                False,
            )
            sys.stdout.flush()
            time.sleep(0.02)

        generator.generate(on_step=on_step)

        print("\033[2J\033[H", end="")
        sys.stdout.flush()
    else:
        generator.generate()

    if not generator.pattern_cells:
        print("Warning: Creating maze without '42' pattern (maze "
              "too small or ENTRY/EXIT overlaps the pattern)")
    generator.solve()
    write_output(generator.maze, generator.path, config)

    return (generator)


def main() -> None:
    """Run the A-Maze-ing program

    Reads the configuration file given on the command line, generates
    and solves the maze, and opens the interactive menu. Exits with
    status 1 if the arguments or the configuration are invalid.
    Ctrl+C and Ctrl+D are caught so the program stops cleanly instead
    of crashing.
    """
    if len(sys.argv) != 2:
        print("Usage: python3 a_maze_ing.py <config_file>")
        sys.exit(1)
    try:
        config = load_config(sys.argv[1])
        can_visualize = validate_maze_size(config.width, config.height)
        generator = generate(config, animate=can_visualize)
        path_cells = pathfinder.path_converter(
            generator.path,
            config.entry,
            config.exit)
        if can_visualize:
            animate_path(
                generator.maze,
                config.entry,
                config.exit,
                path_cells,
                generator.pattern_cells,
                COLOR_THEMES["green"])
            show_menu(generator.maze, config.entry, config.exit,
                      path_cells, generator.pattern_cells, config)
    except ConfigError as e:
        print(e)
        sys.exit(1)
    except (KeyboardInterrupt, EOFError):
        print("\nInterrupted by user, Exiting")
        sys.exit(0)


if __name__ == "__main__":
    main()
