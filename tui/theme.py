from __future__ import annotations

from dataclasses import dataclass
from typing import Literal, Tuple


Align = Literal["left", "center", "right"]


@dataclass(frozen=True, slots=True)
class BarStyle:
    """Style config for a header/footer bar.

    Args:
        fg: ANSI SGR foreground color code (e.g., 97).
        bg: ANSI SGR background color code (e.g., 44).
        align: Text alignment within the bar: left/center/right.
        attrs: Optional additional SGR attributes (e.g., 1 for bold).
    """

    fg: int = 97
    bg: int = 44
    align: Align = "center"
    attrs: Tuple[int, ...] = ()

    def sgr(self) -> str:
        """Return the ANSI SGR escape sequence for this bar."""
        # Order is not critical, but keeping attrs first is conventional.
        return Theme.sgr(*self.attrs, self.fg, self.bg)


@dataclass(frozen=True, slots=True)
class Theme:
    """Theme configuration for ANSI rendering."""

    header: BarStyle
    footer: BarStyle
    reset: str = "\x1b[0m"

    @staticmethod
    def sgr(*codes: int) -> str:
        """Build an ANSI SGR escape sequence from integer codes."""
        joined = ";".join(str(c) for c in codes)
        return f"\x1b[{joined}m"


def default_theme() -> Theme:
    """Default theme: blue background + white text.

    - Header aligned center
    - Footer aligned left
    """
    header = BarStyle(fg=97, bg=44, align="center")
    footer = BarStyle(fg=30, bg=47, align="left")
    return Theme(header=header, footer=footer)
