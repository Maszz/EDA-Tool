import dash
from dash import html
import dash_bootstrap_components as dbc

dash.register_page(__name__, path="/", title="Data Overview")


def layout(**kwargs: dict[str, str]) -> "html.Div":
    return dbc.Container(
        [
            html.H1("📋 Data Overview", className="display-4 text-center"),
            html.P(
                "Explore your dataset by checking the preview and missing values.",
                className="lead text-muted text-center",
            ),
            # Data Preview (First 10 Records)
            dbc.Row(
                [
                    dbc.Col(
                        dbc.Card(
                            [
                                dbc.CardHeader(
                                    "Top 10 Record Preview",
                                    className="bg-primary text-white",
                                ),
                                dbc.CardBody(html.Div(id="output-table")),
                            ],
                            className="shadow-sm",
                        ),
                        width=10,
                    ),
                ],
                className="justify-content-center mb-4",
            ),
            # Dataset Summary (Data Types & Missing Values)
            dbc.Row(
                [
                    dbc.Col(
                        dbc.Card(
                            [
                                dbc.CardHeader(
                                    "Dataset Summary (Data Types & Missing Values)",
                                    className="bg-dark text-white",
                                ),
                                dbc.CardBody(html.Div(id="data-summary")),
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
