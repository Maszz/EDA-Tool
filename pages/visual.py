import dash
import dash_bootstrap_components as dbc
from dash import dcc, html

dash.register_page(__name__, path="/visualization", title="Visualization")


def layout(**kwargs: dict[str, str]) -> "html.Div":
    return dbc.Container(
        [
            html.H1("📊 Data Visualization", className="display-4 text-center"),
            html.P(
                "Use various visualizations to explore relationships between features and understand your dataset better.",
                className="lead text-muted text-center",
            ),
            # Feature Relationships (Scatter Plot + Pair Plot in the Same Row)
            dbc.Row(
                [
                    dbc.Col(
                        dbc.Card(
                            [
                                dbc.CardHeader("Feature Relationships (Scatter Plot)"),
                                dbc.CardBody(
                                    [
                                        html.P(
                                            "Select two numerical features to visualize their relationship:",
                                            className="text-muted",
                                        ),
                                        # X & Y Dropdowns (Stacked)
                                        dcc.Dropdown(
                                            id="feature-x-dropdown",
                                            placeholder="Select a feature for X-axis...",
                                            className="dropdown-style mb-2",
                                        ),
                                        dcc.Dropdown(
                                            id="feature-y-dropdown",
                                            placeholder="Select a feature for Y-axis...",
                                            className="dropdown-style mb-3",
                                        ),
                                        dbc.Row(
                                            [
                                                html.Label(
                                                    "Select Plot Type:",
                                                    className="fw-bold mb-2",
                                                ),
                                                dbc.RadioItems(
                                                    id="scatter-contour-toggle",
                                                    options=[
                                                        {
                                                            "label": "🔵 Scatter Plot",
                                                            "value": "scatter",
                                                        },
                                                        {
                                                            "label": "🔶 Contour Plot",
                                                            "value": "contour",
                                                        },
                                                    ],
                                                    value="scatter",  # Default to Scatter Plot
                                                    inline=True,
                                                    className="mb-3",
                                                    labelClassName="me-3 text-primary",  # Adds spacing & color
                                                    inputClassName="me-2",  # Adds space between radio button and text
                                                ),
                                            ],
                                            className="mb-3 d-flex align-items-center",
                                        ),
                                        dcc.Loading(
                                            type="circle",
                                            children=[dcc.Graph(id="scatter-plot")],
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
                                    "Pairwise Feature Interactions (Pair Plot)"
                                ),
                                dbc.CardBody(
                                    [
                                        html.P(
                                            "Select multiple numerical features to analyze their interactions using a pair plot:",
                                            className="text-muted",
                                        ),
                                        dcc.Dropdown(
                                            id="pairplot-features-dropdown",
                                            multi=True,
                                            placeholder="Select multiple features...",
                                            className="dropdown-style mb-3",
                                        ),
                                        dcc.Loading(
                                            type="circle",
                                            children=[dcc.Graph(id="pair-plot")],
                                        ),
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
            # Categorical Feature Distributions (Bar Plot & Violin Plot)
            dbc.Row(
                dbc.Col(
                    dbc.Card(
                        [
                            dbc.CardHeader("Categorical Feature Distributions"),
                            dbc.CardBody(
                                [
                                    html.P(
                                        "Select a categorical feature to explore its distribution using bar and violin plots:",
                                        className="text-muted",
                                    ),
                                    dbc.Row(
                                        [
                                            dbc.Col(
                                                dcc.Dropdown(
                                                    id="categorical-dropdown",
                                                    placeholder="Select a categorical feature...",
                                                    className="dropdown-style mb-3",
                                                ),
                                                width=6,
                                            ),
                                            dbc.Col(
                                                dcc.Dropdown(
                                                    id="numeric-dropdown",
                                                    placeholder="Select a numerical feature...",
                                                    className="dropdown-style mb-3",
                                                ),
                                                width=6,
                                            ),
                                        ]
                                    ),
                                    dbc.Row(
                                        [
                                            dbc.Col(
                                                dcc.Loading(
                                                    type="circle",
                                                    children=[dcc.Graph(id="bar-plot")],
                                                ),
                                                width=6,
                                            ),
                                            dbc.Col(
                                                dcc.Loading(
                                                    type="circle",
                                                    children=[
                                                        dcc.Graph(id="violin-plot")
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
            # Multivariate Analysis (Parallel Coordinates + PCA Contour)
            dbc.Row(
                [
                    dbc.Col(
                        dbc.Card(
                            [
                                dbc.CardHeader(
                                    "Multivariate Relationships (Parallel Coordinates)"
                                ),
                                dbc.CardBody(
                                    [
                                        html.P(
                                            "Select multiple numerical features to visualize how they relate to each other:",
                                            className="text-muted",
                                        ),
                                        dcc.Dropdown(
                                            id="multivariate-features-dropdown",
                                            multi=True,
                                            placeholder="Select multiple features...",
                                            className="dropdown-style mb-3",
                                        ),
                                        dcc.Loading(
                                            type="circle",
                                            children=[
                                                dcc.Graph(id="parallel-coordinates")
                                            ],
                                        ),
                                    ]
                                ),
                            ],
                            className="shadow-sm",
                        ),
                        width=6,
                    ),
                    dbc.Col(
                        width=6,
                    ),
                ],
                className="mb-4",
            ),
        ],
        fluid=True,
        className="p-4",
    )
