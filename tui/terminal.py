from __future__ import annotations

import sys
import termios
from dataclasses import dataclass
from typing import Optional


ESC = "\x1b["


@dataclass(slots=True)
class TerminalSession:
    """Manage terminal lifecycle safely (context manager).

    - Disables canonical mode and echo (no need to press Enter; keys won't echo).
    - Keeps ISIG enabled (Ctrl+C still works).
    - Optionally uses the alternate screen buffer.
    - Hides cursor on enter, restores it on exit.
    """

    use_alt_screen: bool = True
    clear_on_exit: bool = False

    _fd: int = -1
    _old_attrs: Optional[list] = None

    def __enter__(self) -> "TerminalSession":
        if not sys.stdin.isatty() or not sys.stdout.isatty():
            raise RuntimeError("TerminalSession requires a TTY (interactive terminal).")

        self._fd = sys.stdin.fileno()
        self._old_attrs = termios.tcgetattr(self._fd)

        new_attrs = termios.tcgetattr(self._fd)

        # new_attrs indices: [iflag, oflag, cflag, lflag, ispeed, ospeed, cc]
        lflag = new_attrs[3]
        lflag &= ~(termios.ECHO | termios.ICANON)  # no echo, no line buffering
        lflag |= termios.ISIG  # keep signals (Ctrl+C)
        new_attrs[3] = lflag

        cc = new_attrs[6]
        cc[termios.VMIN] = 0
        cc[termios.VTIME] = 0
        new_attrs[6] = cc

        termios.tcsetattr(self._fd, termios.TCSADRAIN, new_attrs)

        if self.use_alt_screen:
            self._write(ESC + "?1049h")  # enter alternate screen buffer

        self._write(ESC + "2J")   # clear screen
        self._write(ESC + "H")    # cursor home
        self._write(ESC + "?25l") # hide cursor
        self._flush()
        return self

    def __exit__(self, exc_type, exc, tb) -> None:
        try:
            self._write("\x1b[0m")   # reset style
            self._write(ESC + "?25h")  # show cursor

            if self.clear_on_exit and not self.use_alt_screen:
                self._write(ESC + "2J")
                self._write(ESC + "H")

            if self.use_alt_screen:
                self._write(ESC + "?1049l")  # leave alternate screen buffer

            self._flush()
        finally:
            if self._old_attrs is not None and self._fd >= 0:
                termios.tcsetattr(self._fd, termios.TCSADRAIN, self._old_attrs)

    @staticmethod
    def _write(data: str) -> None:
        sys.stdout.write(data)

    @staticmethod
    def _flush() -> None:
        sys.stdout.flush()
