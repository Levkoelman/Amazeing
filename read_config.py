from pydantic import (
    BaseModel,
    Field,
    model_validator,
    field_validator,
    ConfigDict,
    ValidationError,
)
from typing import Optional, Any


class ConfigError(Exception):
    """Raised when the config file cannot be read or contains invalid data."""


def read_config(file_name: str) -> dict[str, str]:
    """Read a config file and parse its KEY=VALUE lines.

    Empty lines and lines starting with '#' are ignored. Spaces around
    keys and values are stripped. Values are returned as strings;
    converting and validating them is left to the caller.

    Args:
        file_name: Path to the config file.

    Returns:
        A dictionary mapping each key to its value.

    Raises:
        ConfigError: If the file cannot be opened or read, a line has
            no '=', a key is empty, or a key appears more than once.
    """
    values: dict[str, str] = {}
    try:
        with open(file_name) as f:
            data = f.read()
    except (OSError, UnicodeDecodeError) as e:
        raise ConfigError(f"Can't open file: {file_name}") from e
    lines = data.splitlines()
    for line in lines:
        line = line.strip()
        if not line or line.startswith("#"):
            continue
        if "=" not in line:
            raise ConfigError(f"Invalid line in {file_name}: "
                              f"{line} (expected KEY=Value)")
        key, value = line.split("=", 1)
        key = key.strip()
        keylower = key.lower()
        if not key:
            raise ConfigError(f'Missing key in {file_name}: '
                              f'"{line}" expected KEY=VALUE')
        value = value.strip()
        if keylower in values:
            raise ConfigError(f"Duplicate key '{key}' in {file_name}")
        values[keylower] = value
    return values


class MazeConfig(BaseModel):
    """Validated settings for generating a maze.

    Built from the dictionary returned by read_config. Unknown keys are
    rejected, ENTRY and EXIT are given as "x,y" and must lie inside the
    maze and differ from each other. Without
    a SEED a random maze is generated.
    """
    model_config = ConfigDict(extra="forbid")

    width: int = Field(gt=1, le=100)
    height: int = Field(gt=1, le=100)
    entry: tuple[int, int]
    exit: tuple[int, int]
    output_file: str = Field(min_length=1)
    perfect: bool
    seed: Optional[int] = None

    @field_validator("entry", "exit", mode='before')
    @classmethod
    def convert(cls, value: Any) -> Any:
        """Turn an "x,y" string into a tuple so pydantic can parse it.

        Spaces around the numbers are removed. Values that are not
        strings are returned unchanged.
        """
        if isinstance(value, str):
            values = value.split(',')
            cutlines = [value.strip() for value in values]
            return tuple(cutlines)
        else:
            return value

    @model_validator(mode='after')
    def check_positions(self) -> 'MazeConfig':
        """Check if entry and exit points are valid.

        Raises:
            ValueError: if entry or exit point is outside of the maze,
                or if the entry point is equal to the exit point.
        """
        x_entry, y_entry = self.entry
        x_exit, y_exit = self.exit
        if (
            x_entry < 0
            or x_entry >= self.width
            or y_entry < 0
            or y_entry >= self.height
        ):
            raise ValueError(f"Entry '{self.entry}' is outside "
                             f"of maze of {self.width} x {self.height}")
        if (
            x_exit < 0
            or x_exit >= self.width
            or y_exit < 0
            or y_exit >= self.height
        ):
            raise ValueError(f"Exit '{self.exit}' is outside "
                             f"of maze of {self.width} x {self.height}")
        if self.entry == self.exit:
            raise ValueError("Entry and exit point cannot be equal")
        if not self.perfect and (self.width < 3 or self.height < 3):
            raise ValueError("PERFECT=False requires a maze of at least 3x3.")
        return self


def load_config(file_path: str) -> MazeConfig:
    """Read and validate a config file.

    Combines read_config and MazeConfig: the file is parsed into a
    dictionary, which is then validated by the model. Only the first
    validation error is reported.

    Args:
        file_path: Path to the config file.

    Returns:
        The validated maze settings.

    Raises:
        ConfigError: if the file cannot be read, a line is invalid, or
            a value fails validation.
    """
    dictionary = read_config(file_path)
    try:
        config = MazeConfig.model_validate(dictionary)
    except ValidationError as e:
        error = e.errors()[0]
        if error["loc"]:
            message = f"{str(error['loc'][0]).upper()}: {error['msg']}"
        else:
            message = error["msg"]
        raise ConfigError(message) from e
    return config
