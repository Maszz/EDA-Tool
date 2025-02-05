import dash
from dash import html, dcc
import dash_bootstrap_components as dbc

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
            # Feature Importance Plot (With Loading Spinner)
            dbc.Row(
                [
                    dbc.Col(
                        dbc.Card(
                            [
                                dbc.CardHeader(
                                    "Feature Importance (ML Explainability)"
                                ),
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
                ],
                className="justify-content-center",
            ),
        ],
        fluid=True,
        className="p-4",
    )
