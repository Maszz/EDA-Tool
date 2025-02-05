import base64
import io

import polars as pl
from dash import Dash, Input, Output, State

from utils.store import Store
from dash import html
import dash


def register_file_callbacks(app: "Dash") -> None:
    """Registers callbacks for reset and file upload handling."""

    @app.callback(
        Output("reset-modal", "is_open"),  # Modal control
        Output(
            "reset-button", "disabled", allow_duplicate=True
        ),  # Disable Clear Button
        Output(
            "file-info", "children", allow_duplicate=True
        ),  # Update status in upload card
        Output(
            "file-upload-status", "data", allow_duplicate=True
        ),  # Reset upload status trigger
        Input("reset-button", "n_clicks"),  # Trigger reset
        Input("confirm-reset", "n_clicks"),  # Confirm reset
        Input("cancel-reset", "n_clicks"),  # Cancel reset
        State("file-upload-status", "data"),  # Check if file uploaded
    )
    def handle_reset_and_modal(
        reset_clicks: int,
        confirm_reset_clicks: int,
        cancel_reset_clicks: int,
        file_uploaded: bool,
    ):
        ctx = dash.ctx.triggered_id  # Identify which input triggered callback

        # If reset button is clicked, open the modal if a file is uploaded
        if ctx == "reset-button":
            if file_uploaded:
                return (
                    True,
                    False,
                    dash.no_update,
                    dash.no_update,
                )  # Open modal, enable button
            return (
                dash.no_update,
                True,
                dash.no_update,
                dash.no_update,
            )  # Keep modal closed, disable button

        # If cancel-reset is clicked, close the modal without resetting
        if ctx == "cancel-reset":
            return False, dash.no_update, dash.no_update, dash.no_update

        no_file_info = html.Div(
            [
                html.P(
                    "📂 No file uploaded yet.",
                    style={"fontWeight": "bold", "color": "#6c757d"},
                ),
                html.P(
                    "⚠️ Please upload a CSV file to start analysis.",
                    style={"color": "#dc3545"},
                ),
            ]
        )
        # If confirm-reset is clicked, clear the stored file and reset the status
        if ctx == "confirm-reset":
            Store.set_static("data_frame", None)  # Clear stored file

            return (
                False,
                True,
                no_file_info,
                False,
            )  # Close modal, disable Clear button, reset status

        # Default case: modal closed, button disabled, no status change
        return False, True, no_file_info, False

    @app.callback(
        Output("file-upload-status", "data"),  # Hidden store to act as a trigger
        Output("file-info", "children"),  # File info display
        Output("file-upload", "contents"),  # Reset file upload contents
        Output("reset-button", "disabled"),  # Enable/disable reset button
        Input("file-upload", "contents"),  # File upload input
        State("file-upload", "filename"),  # File name input
        prevent_initial_call=True,
    )
    def handle_file_upload(contents: str, filename: str):
        """Handles file upload logic, stores file in memory, and manages reset button state."""

        if contents is not None:
            content_type, content_string = contents.split(",")
            decoded = base64.b64decode(content_string)

            try:
                if filename.endswith(".csv"):
                    # Read and store the file in memory
                    df = pl.read_csv(io.StringIO(decoded.decode("utf-8")))
                    Store.set_static("data_frame", df)

                    # File info display
                    file_info = html.Div(
                        [
                            html.P(
                                f"📄 {filename} ({len(decoded) / 1024:.2f} KB)",
                                style={"fontWeight": "bold"},
                            ),
                            html.P(
                                "✅ File uploaded successfully!",
                                style={"color": "green"},
                            ),
                        ]
                    )

                    # Enable reset button when a file is successfully uploaded
                    return True, file_info, None, False

                # Unsupported file type
                return False, "Unsupported file type.", None, True

            except Exception as e:
                # Handle errors gracefully
                return False, f"Error: {e!s}", None, True

        # No file uploaded
        return False, "No file uploaded yet.", None, True

    # @app.callback(
    #     Output("output-table", "children", allow_duplicate=True),
    #     Input("reset-button", "n_clicks"),
    # )
    # def reset_button(n_clicks: int) -> str:
    #     if n_clicks > 0:
    #         Store.set_static("data_frame", None)
    #         return "No file uploaded yet."

    #     return "No file uploaded yet."
