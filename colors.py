"""ANSI color helpers."""

from colorama import init

init(autoreset=True)


class Palette:
    """Named ANSI colors and helpers to apply them to text."""

    RESET: str = "\033[0m"
    DEFAULT: str = "white"

    @staticmethod
    def _c256(n: int) -> str:
        """ANSI 256-color foreground code."""
        return f"\033[38;5;{n}m"

    TABLE: dict[str, str] = {
        "black": "\033[30m", "red": "\033[31m", "green": "\033[32m",
        "yellow": "\033[33m", "blue": "\033[34m", "magenta": "\033[35m",
        "cyan": "\033[36m", "white": "\033[37m",
        # bright variants
        "gray": "\033[90m", "lightred": "\033[91m",
        "lightgreen": "\033[92m", "lightyellow": "\033[93m",
        "lightblue": "\033[94m", "lightmagenta": "\033[95m",
        "lightcyan": "\033[96m", "lightwhite": "\033[97m",
        # dark variants
        "darkred": _c256(52), "darkgreen": _c256(22),
        "darkblue": _c256(17), "darkyellow": _c256(136),
        "darkmagenta": _c256(90), "darkcyan": _c256(23),
        "darkgray": _c256(238), "darkorange": _c256(166),
        "darkpurple": _c256(53), "darkpink": _c256(132),
        "darklime": _c256(70), "darkgold": _c256(178),
        "darkturquoise": _c256(37), "darkviolet": _c256(91),
        "darkcrimson": _c256(125), "darksalmon": _c256(173),
        "darkcoral": _c256(167),
        # extra
        "orange": _c256(208), "purple": _c256(93), "pink": _c256(213),
        "brown": _c256(94), "gold": _c256(220), "lime": _c256(118),
        "teal": _c256(30), "maroon": _c256(88), "navy": _c256(18),
        "olive": _c256(100), "violet": _c256(129),
        "crimson": _c256(161), "turquoise": _c256(45),
        "salmon": _c256(209), "beige": _c256(223),
        "silver": _c256(250), "coral": _c256(203),
        "indigo": _c256(54), "rainbow": _c256(196),
    }

    @classmethod
    def has(cls, name: str) -> bool:
        """Tell whether a color name exists (case-insensitive)."""
        return name.lower() in cls.TABLE

    @classmethod
    def names(cls) -> list[str]:
        """Return all known color names."""
        return list(cls.TABLE)

    @classmethod
    def get(cls, name: str) -> str:
        """Return the ANSI code for a color name (case-insensitive)."""
        return cls.TABLE[name.lower()]

    @classmethod
    def colorize(cls, text: str, color: str = "") -> str:
        """Wrap text in the given color (white if empty)."""
        code = cls.get(color or cls.DEFAULT)
        return f"{code}{text}{cls.RESET}"


COLORS = Palette.TABLE
RESET = Palette.RESET
