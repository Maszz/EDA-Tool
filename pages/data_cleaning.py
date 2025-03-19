import dash
import dash_bootstrap_components as dbc
from dash import dcc, html, Input, Output, State
import pandas as pd
import numpy as np

dash.register_page(__name__, path="/data-cleaning", title="Data Cleaning")


def layout(**kwargs: dict[str, str]) -> "html.Div":
    return dbc.Container(
        [
            html.H1("🧹 Data Cleaning", className="display-4 text-center"),
            html.P(
                "Clean your dataset by handling missing values, outliers, and data inconsistencies.",
                className="lead text-muted text-center",
            ),
            # Data Cleaning Options
            dbc.Row(
                [
                    dbc.Col(
                        dbc.Card(
                            [
                                dbc.CardHeader(
                                    "Missing Values Treatment",
                                    className="bg-info text-white",
                                ),
                                dbc.CardBody(
                                    [
                                        html.Label("Select Column:"),
                                        dcc.Dropdown(id="column-select-missing"),
                                        html.Label("Treatment Method:"),
                                        dcc.Dropdown(
                                            id="missing-treatment-method",
                                            options=[
                                                {"label": "Mean", "value": "mean"},
                                                {"label": "Median", "value": "median"},
                                                {"label": "Mode", "value": "mode"},
                                                {"label": "Drop Rows", "value": "drop"},
                                            ],
                                        ),
                                        dbc.Button(
                                            "Apply Treatment",
                                            id="apply-missing-treatment",
                                            color="primary",
                                            className="mt-3",
                                        ),
                                    ]
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
                                    "Outlier Detection",
                                    className="bg-warning text-white",
                                ),
                                dbc.CardBody(
                                    [
                                        html.Label("Select Column:"),
                                        dcc.Dropdown(id="column-select-outlier"),
                                        html.Label("Method:"),
                                        dcc.Dropdown(
                                            id="outlier-method",
                                            options=[
                                                {"label": "IQR Method", "value": "iqr"},
                                                {"label": "Z-Score", "value": "zscore"},
                                            ],
                                        ),
                                        dbc.Button(
                                            "Detect Outliers",
                                            id="detect-outliers",
                                            color="warning",
                                            className="mt-3",
                                        ),
                                    ]
                                ),
                            ],
                            className="shadow-sm",
                        ),
                        width=6,
                    ),
                ],
                className="justify-content-center mb-4",
            ),
            # Data Type Conversion
            dbc.Row(
                [
                    dbc.Col(
                        dbc.Card(
                            [
                                dbc.CardHeader(
                                    "Data Type Conversion",
                                    className="bg-success text-white",
                                ),
                                dbc.CardBody(
                                    [
                                        html.Label("Select Column:"),
                                        dcc.Dropdown(id="column-select-type"),
                                        html.Label("Convert To:"),
                                        dcc.Dropdown(
                                            id="type-conversion",
                                            options=[
                                                {
                                                    "label": "Numeric",
                                                    "value": "numeric",
                                                },
                                                {
                                                    "label": "Categorical",
                                                    "value": "categorical",
                                                },
                                                {"label": "Date", "value": "date"},
                                            ],
                                        ),
                                        dbc.Button(
                                            "Convert Type",
                                            id="convert-type",
                                            color="success",
                                            className="mt-3",
                                        ),
                                    ]
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
                                    "Duplicate Handling",
                                    className="bg-danger text-white",
                                ),
                                dbc.CardBody(
                                    [
                                        html.Label(
                                            "Select Columns for Duplicate Check:"
                                        ),
                                        dcc.Dropdown(
                                            id="duplicate-columns",
                                            multi=True,
                                        ),
                                        dbc.Button(
                                            "Remove Duplicates",
                                            id="remove-duplicates",
                                            color="danger",
                                            className="mt-3",
                                        ),
                                    ]
                                ),
                            ],
                            className="shadow-sm",
                        ),
                        width=6,
                    ),
                ],
                className="justify-content-center mb-4",
            ),
            # Results Display
            dbc.Row(
                [
                    dbc.Col(
                        dbc.Card(
                            [
                                dbc.CardHeader(
                                    "Cleaned Data Preview",
                                    className="bg-primary text-white",
                                ),
                                dbc.CardBody(
                                    dcc.Loading(
                                        type="circle",
                                        children=[html.Div(id="cleaned-data-preview")],
                                    )
                                ),
                            ],
                            className="shadow-sm",
                        ),
                        width=12,
                    ),
                ],
                className="justify-content-center mb-4",
            ),
        ],
        fluid=True,
        class_name="p-4",
    )
