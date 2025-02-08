import dash
import dash_bootstrap_components as dbc
from dash import html, dcc

dash.register_page(__name__, path="/statistics", title="Statistics")


def layout(**kwargs: dict[str, str]) -> "html.Div":
    return dbc.Container(
        [
            html.H1("📊 Statistics", className="display-4 text-center"),
            html.P(
                "Check the statistical summary, feature distribution, outlier detection, correlation analysis, and skewness/kurtosis.",
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
                                dbc.CardBody(
                                    dcc.Loading(
                                        type="circle",
                                        children=[html.Div(id="stats-table")],
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
            # Feature Analysis Section (Includes Distribution, Outliers, Skewness & KDE)
            dbc.Row(
                [
                    dbc.Col(
                        dbc.Card(
                            [
                                dbc.CardHeader("Feature Analysis"),
                                dbc.CardBody(
                                    [
                                        # Sticky Feature Selection Dropdown (Offset for Navbar)
                                        html.Div(
                                            dcc.Dropdown(
                                                id="column-dropdown",
                                                placeholder="Select a feature for analysis...",
                                                className="dropdown-style",
                                            ),
                                            className="mb-4",
                                            style={
                                                "position": "sticky",  # Sticky when scrolling
                                                "top": "65px",  # Offset below navbar
                                                "zIndex": "1000",  # Ensures it's above other content
                                                "backgroundColor": "white",
                                                "padding": "10px",
                                                "boxShadow": "0px 4px 6px rgba(0, 0, 0, 0.1)",
                                            },
                                        ),
                                        dbc.Row(
                                            [
                                                # Feature Distribution
                                                dbc.Col(
                                                    dbc.Card(
                                                        [
                                                            dbc.CardHeader(
                                                                "Feature Distribution",
                                                                className="bg-primary text-white",
                                                            ),
                                                            dbc.CardBody(
                                                                dcc.Loading(
                                                                    type="circle",
                                                                    children=[
                                                                        dcc.Graph(
                                                                            id="distribution-plot"
                                                                        )
                                                                    ],
                                                                )
                                                            ),
                                                        ],
                                                        className="shadow-sm",
                                                    ),
                                                    width=6,
                                                ),
                                                # Outlier Detection
                                                dbc.Col(
                                                    dbc.Card(
                                                        [
                                                            dbc.CardHeader(
                                                                "Outlier Detection",
                                                                className="bg-danger text-white",
                                                            ),
                                                            dbc.CardBody(
                                                                [
                                                                    # Dropdown for Outlier Detection Algorithm
                                                                    dcc.Dropdown(
                                                                        id="outlier-algo-dropdown",
                                                                        options=[
                                                                            {
                                                                                "label": "Z-Score",
                                                                                "value": "zscore",
                                                                            },
                                                                            {
                                                                                "label": "IQR",
                                                                                "value": "iqr",
                                                                            },
                                                                            {
                                                                                "label": "DBSCAN",
                                                                                "value": "dbscan",
                                                                            },
                                                                            {
                                                                                "label": "Isolation Forest",
                                                                                "value": "isolation_forest",
                                                                            },
                                                                        ],
                                                                        value="zscore",
                                                                        placeholder="Select an outlier detection algorithm...",
                                                                        className="dropdown-style mb-3",
                                                                    ),
                                                                    dcc.Loading(
                                                                        type="circle",
                                                                        children=[
                                                                            dcc.Graph(
                                                                                id="outlier-boxplot"
                                                                            )
                                                                        ],
                                                                    ),
                                                                ]
                                                            ),
                                                        ],
                                                        className="shadow-sm",
                                                    ),
                                                    width=6,
                                                ),
                                            ]
                                        ),
                                        html.Hr(),
                                        # Skewness, Kurtosis, and KDE inside the same card
                                        dbc.Row(
                                            [
                                                # Skewness & Kurtosis Table
                                                dbc.Col(
                                                    dbc.Card(
                                                        [
                                                            dbc.CardHeader(
                                                                "Skewness & Kurtosis"
                                                            ),
                                                            dbc.CardBody(
                                                                dcc.Loading(
                                                                    type="circle",
                                                                    children=[
                                                                        html.Div(
                                                                            id="skewness-kurtosis-table"
                                                                        )
                                                                    ],
                                                                )
                                                            ),
                                                        ],
                                                        className="shadow-sm",
                                                    ),
                                                    width=6,
                                                ),
                                                # KDE Plot
                                                dbc.Col(
                                                    dbc.Card(
                                                        [
                                                            dbc.CardHeader(
                                                                "Kernel Density Estimation (KDE)",
                                                                className="bg-info text-white",
                                                            ),
                                                            dbc.CardBody(
                                                                dcc.Loading(
                                                                    type="circle",
                                                                    children=[
                                                                        dcc.Graph(
                                                                            id="kde-plot"
                                                                        )
                                                                    ],
                                                                )
                                                            ),
                                                        ],
                                                        className="shadow-sm",
                                                    ),
                                                    width=6,
                                                ),
                                            ]
                                        ),
                                    ]
                                ),
                            ],
                            className="shadow-sm",
                        ),
                        width=12,
                    ),
                ],
                className="mb-4",
            ),
            html.Hr(),
            # Correlation Heatmap (Your Existing Code)
            dbc.Row(
                [
                    dbc.Col(
                        dbc.Card(
                            [
                                dbc.CardHeader("Feature Correlation Heatmap"),
                                dbc.CardBody(
                                    [
                                        # Dropdown for Correlation Method
                                        dcc.Dropdown(
                                            id="correlation-method-dropdown",
                                            options=[
                                                {
                                                    "label": "Pearson",
                                                    "value": "pearson",
                                                },
                                                {
                                                    "label": "Spearman",
                                                    "value": "spearman",
                                                },
                                                {
                                                    "label": "Kendall",
                                                    "value": "kendall",
                                                },
                                            ],
                                            value="pearson",
                                            placeholder="Select correlation method...",
                                            className="dropdown-style mb-3",
                                        ),
                                        dcc.Loading(
                                            type="circle",
                                            children=[
                                                dcc.Graph(id="correlation-heatmap")
                                            ],
                                        ),
                                    ]
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
        className="p-4",
    )
