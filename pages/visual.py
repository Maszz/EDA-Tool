import dash
from dash import html, dcc
import dash_bootstrap_components as dbc

dash.register_page(__name__, path="/visuals", title="Visualizations")


def layout(**kwargs: dict[str, str]) -> "html.Div":
    return dbc.Container(
        [
            html.H1("📈 Visualizations", className="display-4 text-center"),
            html.P(
                "Explore feature distributions, outliers, and correlations.",
                className="lead text-muted text-center",
            ),
            # Dropdown for Feature Selection
            html.Div(
                dcc.Dropdown(
                    id="column-dropdown",
                    placeholder="Select a feature for analysis...",
                    className="dropdown-style",
                ),
                className="mb-4",
            ),
            # Feature Analysis Section
            dbc.Row(
                [
                    # Feature Distribution
                    dbc.Col(
                        dbc.Card(
                            [
                                dbc.CardHeader("Feature Distribution"),
                                dbc.CardBody(dcc.Graph(id="distribution-plot")),
                            ],
                            className="shadow-sm",
                        ),
                        width=6,
                    ),
                    # Outlier Detection
                    dbc.Col(
                        dbc.Card(
                            [
                                dbc.CardHeader("Outlier Detection"),
                                dbc.CardBody(
                                    [
                                        # Dropdown for Outlier Detection Algorithm
                                        dcc.Dropdown(
                                            id="outlier-algo-dropdown",
                                            options=[
                                                {"label": "Z-Score", "value": "zscore"},
                                                {"label": "IQR", "value": "iqr"},
                                                {"label": "DBSCAN", "value": "dbscan"},
                                                {
                                                    "label": "Isolation Forest",
                                                    "value": "isolation_forest",
                                                },
                                            ],
                                            value="zscore",
                                            placeholder="Select an outlier detection algorithm...",
                                            className="dropdown-style mb-3",
                                        ),
                                        dcc.Graph(id="outlier-boxplot"),
                                    ]
                                ),
                            ],
                            className="shadow-sm",
                        ),
                        width=6,
                    ),
                ],
                className="mb-4",
            ),
            # Correlation Heatmap
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
                                        dcc.Graph(id="correlation-heatmap"),
                                    ]
                                ),
                            ],
                            className="shadow-sm",
                        ),
                        width=12,
                    ),
                ]
            ),
        ],
        fluid=True,
        className="p-4",
    )
