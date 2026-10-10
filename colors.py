"""ANSI color helpers."""

from colorama import init

init(autoreset=True)

RESET = "\033[0m"


def _c256(n: int) -> str:
    """ANSI 256-color foreground code."""
    return f"\033[38;5;{n}m"


COLORS: dict[str, str] = {
    "black": "\033[30m", "red": "\033[31m", "green": "\033[32m",
    "yellow": "\033[33m", "blue": "\033[34m", "magenta": "\033[35m",
    "cyan": "\033[36m", "white": "\033[37m",
    # bright variants
    "gray": "\033[90m", "lightred": "\033[91m", "lightgreen": "\033[92m",
    "lightyellow": "\033[93m", "lightblue": "\033[94m",
    "lightmagenta": "\033[95m", "lightcyan": "\033[96m",
    "lightwhite": "\033[97m",
    # extra
    "orange": _c256(208), "purple": _c256(93), "pink": _c256(213),
    "brown": _c256(94), "gold": _c256(220), "lime": _c256(118),
    "teal": _c256(30), "maroon": _c256(88), "navy": _c256(18),
    "olive": _c256(100), "violet": _c256(129), "crimson": _c256(161),
    "turquoise": _c256(45), "salmon": _c256(209), "beige": _c256(223),
    "silver": _c256(250), "coral": _c256(203), "indigo": _c256(54),
    "rainbow": _c256(196),
}


def get_color(name: str) -> str:
    """Return the ANSI code for a color name (case-insensitive)."""
    return COLORS[name.lower()]


def colorize(text: str, color: str) -> str:
    """Wrap text in the given color."""
    return f"{get_color(color)}{text}{RESET}"