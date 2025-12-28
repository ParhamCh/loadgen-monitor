from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from typing import Sequence


@dataclass(slots=True)
class AppState:
    """Application state (Model).

    Keep this structure minimal and explicit. As the UI grows, add only
    fields that are required for rendering and interaction.
    """

    running: bool = True
    now: datetime = field(default_factory=datetime.now)
    width: int = 80
    height: int = 24

    header_text: str = ""
    footer_text: str = ""
    body_lines: Sequence[str] = field(default_factory=tuple)

    counter: int = 0
