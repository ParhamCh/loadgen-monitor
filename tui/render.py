from __future__ import annotations

from dataclasses import dataclass
from typing import Protocol

from .model import AppState
from .theme import Theme, Align


ESC = "\x1b["


class Renderer(Protocol):
    """Renderer strategy interface."""

    def render(self, state: AppState) -> str:
        """Return a full-frame string for the terminal."""
        raise NotImplementedError


@dataclass(slots=True)
class AnsiFixedLayoutRenderer:
    """ANSI renderer with fixed header/body/footer and double buffering."""

    theme: Theme

    def render(self, state: AppState) -> str:
        width = max(1, state.width)
        height = max(1, state.height)

        header = self._bar_line(
            width=width,
            title=state.header_text,
            sgr=self.theme.header.sgr(),
            align=self.theme.header.align,
            reset=self.theme.reset,
        )

        footer = self._bar_line(
            width=width,
            title=state.footer_text,
            sgr=self.theme.footer.sgr(),
            align=self.theme.footer.align,
            reset=self.theme.reset,
        )

        body_h = max(0, height - 2)
        body_lines = list(state.body_lines) if state.body_lines else [""]
        body_out = []
        for i in range(body_h):
            text = body_lines[i] if i < len(body_lines) else ""
            body_out.append(self._body_line(width, text))

        lines = [header] + body_out
        if height >= 2:
            lines.append(footer)

        lines = lines[:height]
        while len(lines) < height:
            lines.append(self._body_line(width, ""))

        cursor_row = 2 if height >= 2 else 1

        return (
            ESC + "H" +
            "\n".join(lines) +
            self.theme.reset +
            f"{ESC}{cursor_row};1H"
        )

    @staticmethod
    def _body_line(width: int, text: str) -> str:
        text = text[:width]
        return text + (" " * max(0, width - len(text)))

    @staticmethod
    def _bar_line(width: int, title: str, sgr: str, align: Align, reset: str) -> str:
        base = " " * width
        title = title[:width]

        if align == "left":
            start = 0
        elif align == "right":
            start = max(0, width - len(title))
        else:  # "center"
            start = max(0, (width - len(title)) // 2)

        line = base[:start] + title + base[start + len(title):]
        return sgr + line + reset
