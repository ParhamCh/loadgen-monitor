from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime


@dataclass(frozen=True, slots=True)
class Event:
    """Base class for all UI events."""


@dataclass(frozen=True, slots=True)
class KeyPress(Event):
    """Represents a single key press (one character)."""

    char: str


@dataclass(frozen=True, slots=True)
class Tick(Event):
    """Represents a periodic tick event (e.g., once per second)."""

    now: datetime


@dataclass(frozen=True, slots=True)
class Resize(Event):
    """Represents a terminal resize event."""

    width: int
    height: int


@dataclass(frozen=True, slots=True)
class Quit(Event):
    """Represents a request to quit the application."""
