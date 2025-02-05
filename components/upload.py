import dash
from dash import dcc, html, callback, Output, Input, State
import dash_bootstrap_components as dbc


def upload_component() -> "html.Div":
    """File upload component with reset confirmation."""

    return dbc.Card(
        [
            # Hidden store to track upload status
            dcc.Store(id="file-upload-status", data=False),
            dcc.Upload(
                id="file-upload",
                children=html.Div(
                    ["📂 Drag and Drop or ", html.A("Select a File")],
                    style={"fontWeight": "bold"},
                ),
                style={
                    "width": "100%",
                    "height": "100px",
                    "lineHeight": "100px",
                    "borderWidth": "2px",
                    "borderStyle": "dashed",
                    "borderRadius": "10px",
                    "textAlign": "center",
                    "margin": "10px",
                    "cursor": "pointer",
                    "backgroundColor": "#f8f9fa",
                    "color": "#007bff",
                },
                multiple=False,
            ),
            html.Div(
                id="file-info", style={"marginTop": "10px", "textAlign": "center"}
            ),
            # html.Div(id="upload-status", style={"display": "none"}),
            dbc.Button(
                "Clear",
                id="reset-button",
                color="danger",
                className="mt-2",
                outline=True,
            ),
            # Confirmation Modal
            dbc.Modal(
                [
                    dbc.ModalHeader("Confirm Reset"),
                    dbc.ModalBody("Are you sure you want to clear the uploaded file?"),
                    dbc.ModalFooter(
                        [
                            dbc.Button(
                                "Cancel",
                                id="cancel-reset",
                                className="me-2",
                                color="secondary",
                            ),
                            dbc.Button(
                                "Yes, Clear",
                                id="confirm-reset",
                                color="danger",
                                className="confirm-btn",
                            ),
                        ]
                    ),
                ],
                id="reset-modal",
                is_open=False,
            ),
        ],
        body=True,
        className="shadow-sm p-3",
    )
