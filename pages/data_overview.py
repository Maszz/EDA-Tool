import dash
from dash import html, dcc
import dash_bootstrap_components as dbc

dash.register_page(__name__, path="/", title="Data Overview")


def layout(**kwargs: dict[str, str]) -> "html.Div":
    return dbc.Container(
        [
            html.H1("📋 Data Overview", className="display-4 text-center"),
            html.P(
                "Explore your dataset by checking the preview, summary, and missing values.",
                className="lead text-muted text-center",
            ),
            # File Summary (Number of Rows & Columns)
            dbc.Row(
                [
                    dbc.Col(
                        dbc.Card(
                            [
                                dbc.CardHeader(
                                    "Dataset Summary", className="bg-info text-white"
                                ),
                                dbc.CardBody(
                                    dcc.Loading(
                                        type="circle",
                                        children=[html.Div(id="file-summary")],
                                    )
                                ),
                            ],
                            className="shadow-sm",
                        ),
                        width=6,
                    ),
                    dbc.Col(
                        dbc.Card(
                            [
                                dbc.CardHeader(
                                    "Duplicate Rows",
                                    className="bg-secondary text-white",
                                ),
                                dbc.CardBody(
                                    dcc.Loading(
                                        type="circle",
                                        children=[html.Div(id="duplicate-rows")],
                                    )
                                ),
                            ],
                            className="shadow-sm",
                        ),
                        width=6,
                    ),
                ],
                className="justify-content-center mb-4",
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
                                dbc.CardBody(
                                    dcc.Loading(
                                        type="circle",
                                        children=[html.Div(id="output-table")],
                                    )
                                ),
                            ],
                            className="shadow-sm",
                        ),
                        width=10,
                    ),
                ],
                className="justify-content-center mb-4",
            ),
            # Dataset Summary & Missing Value Histogram
            dbc.Row(
                [
                    # Dataset Summary (Data Types & Missing Values)
                    dbc.Col(
                        dbc.Card(
                            [
                                dbc.CardHeader(
                                    "Data Types & Missing Values",
                                    className="bg-dark text-white",
                                ),
                                dbc.CardBody(
                                    dcc.Loading(
                                        type="circle",
                                        children=[html.Div(id="data-summary")],
                                    )
                                ),
                            ],
                            className="shadow-sm",
                        ),
                        width=6,
                    ),
                    # Missing Value Histogram
                    dbc.Col(
                        dbc.Card(
                            [
                                dbc.CardHeader(
                                    "Missing Data Patterns",
                                    className="bg-danger text-white",
                                ),
                                dbc.CardBody(
                                    dcc.Loading(
                                        type="circle",
                                        children=[dcc.Graph(id="missing-value-heat")],
                                    )
                                ),
                            ],
                            className="shadow-sm",
                        ),
                        width=6,
                    ),
                ],
                className="justify-content-center mb-4",
            ),
        ],
        fluid=True,
        className="p-4",
    )
