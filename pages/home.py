import dash
from dash import html

from components.upload import upload_component

dash.register_page(__name__, path="/", title="Home")


def layout(**kwargs: dict[str, str]) -> "html.Div":
    return html.Div(
        [
            html.H1("Scalable Dash App"),
            upload_component(),
            html.Button("Reset", id="reset-button", n_clicks=0),
            html.Div(id="output-table"),
        ],
    )
