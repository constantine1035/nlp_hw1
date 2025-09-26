from __future__ import annotations

import reflex as rx  # type: ignore

from .components import index

# Import the state module so that Reflex can discover and register the
# custom ``State`` class defined there.  In recent Reflex versions the
# application is instantiated without passing a state argument; the
# framework automatically tracks any state classes that are imported
# before the app is created.
from . import state  # noqa: F401  # ensure State is registered

app = rx.App()

app.add_page(index, route="/")
