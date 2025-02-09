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
                dbc.Col(
                    dbc.Card(
                        [
                            dbc.CardHeader(
                                "Statistical Summary",
                                className="bg-secondary text-white",
                            ),
                            dbc.CardBody(
                                dcc.Loading(
                                    type="circle", children=[html.Div(id="stats-table")]
                                )
                            ),
                        ],
                        className="shadow-sm",
                    ),
                    width=12,
                ),
                className="justify-content-center mb-4",
            ),
            # Feature Analysis Section
            dbc.Row(
                dbc.Col(
                    dbc.Card(
                        [
                            dbc.CardHeader("Feature Analysis"),
                            dbc.CardBody(
                                [
                                    # Sticky Feature Selection Dropdown
                                    html.Div(
                                        dcc.Dropdown(
                                            id="column-dropdown",
                                            placeholder="Select a feature for analysis...",
                                            className="dropdown-style",
                                        ),
                                        className="mb-3",
                                        style={
                                            "position": "sticky",
                                            "top": "65px",
                                            "zIndex": "1000",
                                            "backgroundColor": "white",
                                            "padding": "10px",
                                            "boxShadow": "0px 4px 6px rgba(0, 0, 0, 0.1)",
                                        },
                                    ),
                                    # Feature Distribution & KDE
                                    dbc.Row(
                                        dbc.Col(
                                            dbc.Card(
                                                [
                                                    dbc.CardHeader(
                                                        "Feature Distribution (Histogram & KDE)",
                                                        className="bg-primary text-white",
                                                    ),
                                                    dbc.CardBody(
                                                        dcc.Loading(
                                                            type="circle",
                                                            children=[
                                                                dcc.Graph(id="kde-plot")
                                                            ],
                                                        )
                                                    ),
                                                ],
                                                className="shadow-sm",
                                            ),
                                            width=12,
                                        ),
                                        className="mb-4",
                                    ),
                                    # Skewness & Kurtosis
                                    dbc.Row(
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
                                            width=12,
                                        ),
                                        className="mb-4",
                                    ),
                                    # Outlier Detection - Boxplot & Scatter Plot Inside the Same Card
                                    dbc.Row(
                                        dbc.Col(
                                            dbc.Card(
                                                [
                                                    dbc.CardHeader(
                                                        "Outlier Detection",
                                                        className="bg-danger text-white",
                                                    ),
                                                    dbc.CardBody(
                                                        [
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
                                                            # Two graphs in the same row inside the card
                                                            dbc.Row(
                                                                [
                                                                    dbc.Col(
                                                                        dcc.Loading(
                                                                            type="circle",
                                                                            children=[
                                                                                dcc.Graph(
                                                                                    id="outlier-boxplot"
                                                                                )
                                                                            ],
                                                                        ),
                                                                        width=6,
                                                                    ),
                                                                    dbc.Col(
                                                                        dcc.Loading(
                                                                            type="circle",
                                                                            children=[
                                                                                dcc.Graph(
                                                                                    id="outlier-scatter"
                                                                                )
                                                                            ],
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
                                        className="mb-4",
                                    ),
                                ]
                            ),
                        ],
                        className="shadow-sm",
                    ),
                    width=12,
                ),
                className="mb-4",
            ),
            # Correlation Heatmap
            dbc.Row(
                dbc.Col(
                    dbc.Card(
                        [
                            dbc.CardHeader("Feature Correlation Heatmap"),
                            dbc.CardBody(
                                [
                                    dcc.Dropdown(
                                        id="correlation-method-dropdown",
                                        options=[
                                            {"label": "Pearson", "value": "pearson"},
                                            {"label": "Spearman", "value": "spearman"},
                                        ],
                                        value="pearson",
                                        placeholder="Select correlation method...",
                                        className="dropdown-style mb-3",
                                    ),
                                    dcc.Loading(
                                        type="circle",
                                        children=[dcc.Graph(id="correlation-heatmap")],
                                    ),
                                ]
                            ),
                        ],
                        className="shadow-sm",
                    ),
                    width=12,
                ),
                className="justify-content-center mb-4",
            ),
        ],
        fluid=True,
        className="p-4",
    )
