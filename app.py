from __future__ import annotations

from datetime import datetime

from tui import (
    AnsiFixedLayoutRenderer,
    AppState,
    InputPoller,
    KeyPress,
    Resize,
    TUIEngine,
    Tick,
    Theme,
    BarStyle,
    default_theme,
)


def update(state: AppState, event) -> AppState:
    if isinstance(event, KeyPress):
        if event.char == "q":
            state.running = False
        return state

    if isinstance(event, Resize):
        state.width = event.width
        state.height = event.height
        return state

    if isinstance(event, Tick):
        state.now = event.now
        state.counter += 1

        state.header_text = state.now.strftime("%H:%M:%S | %Y-%m-%d | %A")
        state.footer_text = "Press 'q' to quit"
        state.body_lines = (
            f"Counter: {state.counter}",
            "",
            "Body region: ready for content...",
        )
        return state

    return state


def main() -> None:
    theme = default_theme()
    renderer = AnsiFixedLayoutRenderer(theme=theme)

    engine = TUIEngine(
        renderer=renderer,
        input_poller=InputPoller(),
        update_fn=update,
        fps=10.0,     # UI refresh ceiling
        tick_hz=1.0,  # counter increments once per second
        use_alt_screen=True,
    )

    initial = AppState()
    engine.run(initial)


if __name__ == "__main__":
    main()
