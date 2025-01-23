from typing import Any

import dash
from dash import html

dash.register_page(__name__)


def layout(**kwargs: dict[str, Any]) -> "html.Div":
    return html.H1("This is our custom 404 content")
