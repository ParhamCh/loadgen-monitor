from __future__ import annotations

import os
import select
import sys
from dataclasses import dataclass
from typing import List

from .events import KeyPress, Event


@dataclass(slots=True)
class InputPoller:
    """Non-blocking input poller based on select().

    Reads available bytes and decodes them as UTF-8 (errors ignored).
    For now, it emits KeyPress events for individual characters.
    """

    read_chunk_size: int = 64

    def poll(self, timeout: float) -> List[Event]:
        """Poll for input events.

        Args:
            timeout: Max seconds to wait. 0 means non-blocking.

        Returns:
            A list of events (KeyPress).
        """
        if timeout < 0:
            timeout = 0.0

        fd = sys.stdin.fileno()
        rlist, _, _ = select.select([fd], [], [], timeout)

        if not rlist:
            return []

        events: List[Event] = []
        while True:
            try:
                data = os.read(fd, self.read_chunk_size)
            except OSError:
                break

            if not data:
                break

            text = data.decode("utf-8", errors="ignore")
            for ch in text:
                events.append(KeyPress(char=ch))

            # If less than chunk size read, we likely drained the buffer.
            if len(data) < self.read_chunk_size:
                break

        return events
