import dash
import dash_bootstrap_components as dbc
from dash import dcc, html

dash.register_page(__name__, path="/feature-importance", title="Feature Importance")


def layout(**kwargs: dict[str, str]) -> "html.Div":
    return dbc.Container(
        [
            # Page Header
            html.H1("🤖 Feature Importance", className="display-4 text-center"),
            html.P(
                "Analyze the importance of each feature in predicting the selected target variable.",
                className="lead text-muted text-center",
            ),
            # Target Selection Dropdown (Centered)
            dbc.Row(
                dbc.Col(
                    html.Div(
                        dcc.Dropdown(
                            id="target-column",
                            placeholder="Select target column...",
                            className="dropdown-style",
                        ),
                        className="mb-4",
                    ),
                    width=6,
                ),
                className="justify-content-center",
            ),
            # Training Status Message
            dbc.Row(
                dbc.Col(
                    html.Div(
                        id="training-status",
                        style={
                            "fontWeight": "bold",
                            "textAlign": "center",
                            "color": "#007bff",
                            "marginBottom": "10px",
                        },
                    ),
                    width=8,
                ),
                className="justify-content-center",
            ),
            # Feature Importance Method Selection + Dynamic Slider
            dbc.Row(
                dbc.Col(
                    dbc.Card(
                        dbc.CardBody(
                            [
                                # Feature Importance Method Selection
                                dcc.Dropdown(
                                    id="importance-method",
                                    options=[
                                        {
                                            "label": "Native Importance (LightGBM)",
                                            "value": "native",
                                        },
                                        {
                                            "label": "Boruta Importance",
                                            "value": "boruta",
                                        },
                                    ],
                                    value="native",  # Default selection
                                    className="dropdown-style mb-3",
                                ),
                                # Dynamic Slider for Selecting Number of Features
                                html.Label(
                                    "Select number of top features:",
                                    className="fw-bold",
                                ),
                                dcc.Slider(
                                    id="num-top-features-slider",
                                    min=2,  # Will be updated dynamically
                                    max=50,  # Will be updated dynamically
                                    step=1,
                                    value=20,  # Default value will be updated dynamically
                                    marks={
                                        2: "2",
                                        5: "5",
                                        10: "10",
                                        15: "15",
                                        20: "20",
                                        25: "25",
                                        30: "30",
                                        35: "35",
                                        40: "40",
                                        45: "45",
                                        50: "50",
                                    },
                                ),
                            ]
                        ),
                        className="shadow-sm",
                    ),
                    width=10,
                ),
                className="justify-content-center mb-4",
            ),
            # Feature Importance Plot
            dbc.Row(
                dbc.Col(
                    dbc.Card(
                        [
                            dbc.CardHeader("Feature Importance (ML Explainability)"),
                            dbc.CardBody(
                                dcc.Loading(  # Show spinner while training
                                    type="circle",
                                    children=[
                                        dcc.Graph(id="feature-importance-plot"),
                                    ],
                                )
                            ),
                        ],
                        className="shadow-sm",
                    ),
                    width=10,
                ),
                className="justify-content-center",
            ),
        ],
        fluid=True,
        className="p-4",
    )
