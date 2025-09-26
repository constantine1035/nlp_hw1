from __future__ import annotations

import reflex as rx  # type: ignore

from .state import State


def ghosted_input(width: str = "100%") -> rx.Component:
    ghost_overlay = rx.box(
        rx.text(
            State.text,
            style={
                "display": "inline",
                "color": "transparent",
                "fontFamily": "ui-monospace, Menlo, Monaco, Consolas, monospace",
                "fontSize": "14px",
                "whiteSpace": "pre-wrap",
            },
        ),
        rx.text(
            State.ghost_suffix,
            style={
                "display": "inline",
                "color": "gray",
                "fontFamily": "ui-monospace, Menlo, Monaco, Consolas, monospace",
                "fontSize": "14px",
                "whiteSpace": "pre-wrap",
            },
        ),
        position="absolute",
        top="0",
        bottom="0",
        left="12px",
        display="flex",
        align_items="center",
        pointer_events="none",
        opacity="0.7",
        z_index="0",
    )

    input_field = rx.input(
        value=State.text,
        placeholder="Начните печатать… (Enter для выбора)",
        on_change=State.update_text,
        on_key_down=State.on_key_down,
        width=width,
        style={"backgroundColor": "transparent"},
        font_family="ui-monospace, Menlo, Monaco, Consolas, monospace",
        font_size="14px",
        z_index="1",
    )

    return rx.box(
        ghost_overlay,
        input_field,
        position="relative",
        width=width,
        border="1px solid var(--gray-6)",
        border_radius="8px",
        padding_y="6px",
    )


def suggestion_strip() -> rx.Component:
    return rx.hstack(
        rx.foreach(
            State.suggestions,
            lambda suggestion: rx.button(
                suggestion,
                size="2",
                variant="solid",
                on_click=lambda _event, suggestion=suggestion: State.apply_suggestion(suggestion),
            ),
        ),
        spacing="2",
        wrap="wrap",
        width="100%",
    )


def index() -> rx.Component:
    return rx.container(
        rx.vstack(
            rx.heading("Text Suggestion Demo", size="8"),
            ghosted_input(width="100%"),
            suggestion_strip(),
            spacing="4",
            width="100%",
        ),
        padding="2em",
    )