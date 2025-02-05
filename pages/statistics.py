import dash
from dash import html
import dash_bootstrap_components as dbc

dash.register_page(__name__, path="/statistics", title="Statistics")


def layout(**kwargs: dict[str, str]) -> "html.Div":
    return dbc.Container(
        [
            html.H1("📊 Statistics", className="display-4 text-center"),
            html.P(
                "Check the statistical summary of your dataset.",
                className="lead text-muted text-center",
            ),
            # Statistical Summary Table
            dbc.Row(
                [
                    dbc.Col(
                        dbc.Card(
                            [
                                dbc.CardHeader(
                                    "Statistical Summary",
                                    className="bg-secondary text-white",
                                ),
                                dbc.CardBody(html.Div(id="stats-table")),
                            ],
                            className="shadow-sm",
                        ),
                        width=10,
                    ),
                ],
                className="justify-content-center mb-4",
            ),
        ],
        fluid=True,
        className="p-4",
    )
