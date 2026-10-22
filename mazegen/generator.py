import random
from .maze_generator import make_grid, make_visited, create_42, create_maze
from .braiding import braiding
from .pathfinder import solve_maze
from typing import Callable, Optional


class MazeGenerator:
    """Generate and solve rectangular mazes.

    The maze is stored as a grid of integers, indexed maze[y][x].
    Each cell holds its closed walls as bits: N=1, E=2, S=4, W=8.

    Attributes:
        maze: The generated grid, empty until generate() is called.
        path: The shortes path from entry to exit as a tring of
            directions, empty until solve() is called.
        pattern_cells: The (x, y) cells of the '42' pattern, empty
            if the pattern did not fit.

    Example:
        >>> generator = MazeGenerator(20, 15, (0, 0), (19, 14), seed=42)
        >>> generator.generate()
        >>> generator.solve()
        >>> print(generator.path)
    """
    def __init__(
        self,
        width: int,
        height: int,
        entry_cell: tuple[int, int],
        exit_cell: tuple[int, int],
        perfect: bool = False,
        seed: Optional[int] = None
    ) -> None:
        """Initialize the maze generator with its settings.

        No maze is created yet: call generate() to build it and
        solve() to find the shortest path.

        Args:
            width: Number of cells in a row.
            height: Number of cells in a colums.
            entry_cell: The (x, y) postition of the entry.
            exit_cell: The (x, y) position of the exit.
            perfect: If True, the maze has exactly one path between
                any two cells. if False, extra walls are removed to
                crate loops. Defaults to False.
            seed: Seed for the random generator. The same seed gives
                the same maze. If None, a random maze is made.
        """
        self.maze: list[list[int]] = []
        self.path: str = ""
        self.pattern_cells: set[tuple[int, int]] = set()
        self._width = width
        self._height = height
        self._entry_cell = entry_cell
        self._exit_cell = exit_cell
        self._perfect = perfect
        self._seed = seed

    def generate(
        self,
        on_step: Optional[
            Callable[[
                list[list[int]],
                set[tuple[int, int]]], None]] = None,
    ) -> None:
        """Generate a new maze and store it in self.maze.

        Builds a grid with all walls closed, places the '42' pattern
        if it fits, and carves the maze with a recursive backtracker.
        If perfect is False, dead ends are opened to create loops.
        Any previous path is cleared.

        After calling this, self.pattern_cells holds the cells of the
        '42' pattern, or is empty if the pattern did not fit.
        """
        random.seed(self._seed)
        self.maze = make_grid(self._width, self._height)
        grid_visited = make_visited(self._width, self._height)
        self.pattern_cells = create_42(
            grid_visited,
            self._entry_cell,
            self._exit_cell
        )

        def report_step() -> None:
            if on_step is not None:
                on_step(self.maze, self.pattern_cells)

        report_step()

        create_maze(
            self.maze,
            grid_visited,
            self._entry_cell,
            on_step=report_step if on_step is not None else None,
        )
        if not self._perfect:
            braiding(self.maze, self.pattern_cells)
            report_step()
        self.path = ""

    def solve(self) -> None:
        """Find the shortes path from entry to exit.

        The path is stored in self.path as a string of directions,
        for example "EESSW" (N = up, E is right, S = down, W = left).

        Raises:
            RuntimeError: If generate() has not been called yet.
        """
        if not self.maze:
            raise RuntimeError("Cannot solve maze before generating.")
        self.path = solve_maze(self.maze, self._entry_cell, self._exit_cell)
