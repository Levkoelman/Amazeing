
from read_config import MazeConfig, ConfigError


def write_output(
    maze: list[list[int]],
    path: str,
    config: MazeConfig
) -> None:
    """Write the maze, entry, exit and shortest path to the output file.

    Args:
        maze: The maze grid, indexed as maze[y][x].
        path: The shortest path, e.g. "EESS".
        config: The settings; entry, exit and output_file are used.

    Raises:
        ConfigError: If the output file cannot be written.
    """
    try:
        with open(config.output_file, "w") as f:
            for row in maze:
                line = ""
                for cell in row:
                    line += f"{cell:X}"
                f.write(f"{line}\n")
            f.write("\n")
            entry_x, entry_y = config.entry
            exit_x, exit_y = config.exit
            f.write(f"{entry_x},{entry_y}\n")
            f.write(f"{exit_x},{exit_y}\n")
            f.write(f"{path}\n")
    except OSError as e:
        raise ConfigError(f"Can't write file: {config.output_file}") from e
