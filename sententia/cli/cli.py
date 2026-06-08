from __future__ import annotations


class ParseCliResult:
    """Data model for CLI argument parsing results.

    Contains all parsed values and the path to the env file.
    """

    pass


def parse_cli_args(argv: list[str] | None = None) -> ParseCliResult:
    """Parse CLI arguments.

    Args:
        argv: List of arguments. None means use sys.argv.

    Returns:
        ParseCliResult with parsed values.
    """
    raise NotImplementedError
