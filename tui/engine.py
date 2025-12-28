from __future__ import annotations

import shutil
import sys
import time
from dataclasses import dataclass
from datetime import datetime
from typing import Callable, Iterable

from .events import Event, KeyPress, Resize, Tick
from .input import InputPoller
from .model import AppState
from .render import Renderer
from .terminal import TerminalSession


UpdateFn = Callable[[AppState, Event], AppState]


@dataclass(slots=True)
class TUIEngine:
    """MVU engine: poll events -> update state -> render.

    The engine is intentionally minimal:
    - Input is polled with a computed timeout (efficient, no busy loop).
    - Tick events are generated at tick_hz (default 1 Hz).
    - Resize events are generated when terminal size changes.
    - Rendering is throttled by fps and only happens when the state is 'dirty'.
    """

    renderer: Renderer
    input_poller: InputPoller
    update_fn: UpdateFn

    fps: float = 10.0
    tick_hz: float = 1.0
    use_alt_screen: bool = True

    def run(self, initial_state: AppState) -> AppState:
        state = initial_state
        dirty = True

        last_w, last_h = self._get_size()
        state.width, state.height = last_w, last_h

        tick_interval = 1.0 / self.tick_hz if self.tick_hz > 0 else 1.0
        render_interval = 1.0 / self.fps if self.fps > 0 else 0.1

        next_tick = time.monotonic()
        next_render = time.monotonic()

        try:
            with TerminalSession(use_alt_screen=self.use_alt_screen):
                self._render(state)

                while state.running:
                    now_m = time.monotonic()
                    timeout = min(next_tick, next_render) - now_m
                    events = self.input_poller.poll(timeout=max(0.0, timeout))

                    w, h = self._get_size()
                    if (w, h) != (last_w, last_h):
                        last_w, last_h = w, h
                        events.append(Resize(width=w, height=h))

                    now_m = time.monotonic()
                    if now_m >= next_tick:
                        events.append(Tick(now=datetime.now()))
                        while next_tick <= now_m:
                            next_tick += tick_interval

                    for ev in events:
                        state = self.update_fn(state, ev)
                    if events:
                        dirty = True

                    now_m = time.monotonic()
                    if dirty and now_m >= next_render:
                        self._render(state)
                        dirty = False
                        next_render = now_m + render_interval

        except KeyboardInterrupt:
            # Exit cleanly on Ctrl+C (no traceback)
            state.running = False

        return state

    def _render(self, state: AppState) -> None:
        sys.stdout.write(self.renderer.render(state))
        sys.stdout.flush()

    @staticmethod
    def _get_size() -> tuple[int, int]:
        size = shutil.get_terminal_size(fallback=(80, 24))
        return size.columns, size.lines
