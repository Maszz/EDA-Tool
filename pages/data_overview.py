import dash
import dash_bootstrap_components as dbc
from dash import dcc, html

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
            # Dataset Summary & ⚠️ Missing Values
            dbc.Row(
                [
                    # Dataset Summary (Data Types)
                    dbc.Col(
                        dbc.Card(
                            [
                                dbc.CardHeader(
                                    "Data Types",
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
                        width=8,
                    ),
                    # ⚠️ Missing Values Summary
                    dbc.Col(
                        dbc.Card(
                            [
                                dbc.CardHeader(
                                    "⚠️ Missing Values",
                                    className="bg-danger text-white",
                                ),
                                dbc.CardBody(
                                    dcc.Loading(
                                        type="circle",
                                        children=[
                                            html.Div(id="missing-values-summary")
                                        ],
                                    )
                                ),
                            ],
                            className="shadow-sm",
                        ),
                        width=4,
                    ),
                ],
                class_name="justify-content-center mb-4",
            ),
        ],
        fluid=True,
        class_name="p-4",
    )
