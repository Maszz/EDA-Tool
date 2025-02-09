import base64
import io

import dash
import polars as pl
from dash import Dash, Input, Output, State, html

from utils.logger_config import logger  # Import logger
from utils.store import Store


def register_file_callbacks(app: "Dash") -> None:
    """Registers callbacks for reset and file upload handling."""

    @app.callback(
        [
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
        ],
        Input("reset-button", "n_clicks"),  # Trigger reset
        Input("confirm-reset", "n_clicks"),  # Confirm reset
        Input("cancel-reset", "n_clicks"),  # Cancel reset
        State("file-upload-status", "data"),  # Check if file uploaded
    )
    def handle_reset_and_modal(
        reset_clicks, confirm_reset_clicks, cancel_reset_clicks, file_uploaded
    ):
        """Handles reset functionality, including modal popups for confirmation."""
        ctx = dash.ctx.triggered_id  # Identify which input triggered callback

        # If reset button is clicked, open the modal if a file is uploaded
        if ctx == "reset-button":
            if file_uploaded:
                logger.info("🧹 Reset button clicked - Opening confirmation modal")
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
            logger.info("🚫 Reset cancelled by user")
            return False, dash.no_update, dash.no_update, dash.no_update

        # If confirm-reset is clicked, clear stored file and reset status
        if ctx == "confirm-reset":
            logger.warning("⚠️ Reset confirmed - Clearing stored file")
            Store.set_static("data_frame", None)  # Clear stored file
            Store.set_static("filename", None)  # Clear stored filename

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

            return (
                False,
                True,
                no_file_info,
                False,
            )  # Close modal, disable Clear button, reset status

        return False, True, dash.no_update, False  # Default case

    @app.callback(
        [
            Output("file-upload-status", "data"),
            Output("file-info", "children"),
            Output("file-upload", "contents"),
            Output("reset-button", "disabled"),
        ],
        Input("file-upload", "contents"),
        State("file-upload", "filename"),
    )
    def handle_file_upload(contents, filename):
        """Handles file upload, stores filename, and prevents unnecessary reloads."""
        # Check if a file is already loaded
        existing_df = Store.get_static("data_frame")
        stored_filename = Store.get_static("filename")

        if not contents:
            if existing_df is not None and stored_filename:
                logger.info(
                    f"📄 {stored_filename} (Already Loaded) - Preventing redundant upload."
                )
                file_info = html.Div(
                    [
                        html.P(
                            f"📄 {stored_filename} (Already Loaded)",
                            style={"fontWeight": "bold"},
                        ),
                        html.P("✅ File is already loaded", style={"color": "green"}),
                    ]
                )
                return [True, file_info, None, False]  # Prevent redundant reloading
            logger.info("📂 No file uploaded yet.")
            return [False, "📂 No file uploaded yet.", None, True]  # No file uploaded

        try:
            # Decode base64 file content
            content_type, content_string = contents.split(",")
            decoded = base64.b64decode(content_string)

            if not filename.endswith(".csv"):
                logger.warning(f"❌ Unsupported file type uploaded: {filename}")
                return [
                    False,
                    "❌ Unsupported file type.",
                    None,
                    True,
                ]  # Unsupported file type

            # Read CSV file using Polars
            df = pl.read_csv(io.StringIO(decoded.decode("utf-8")))

            # Store DataFrame and filename
            Store.set_static("data_frame", df)
            Store.set_static("filename", filename)

            logger.info(f"✅ File uploaded: {filename}, Shape: {df.shape}")

            file_info = html.Div(
                [
                    html.P(
                        f"📄 {filename} ({len(decoded) / 1024:.2f} KB)",
                        style={"fontWeight": "bold"},
                    ),
                    html.P("✅ File uploaded successfully!", style={"color": "green"}),
                ]
            )

            return [True, file_info, None, False]  # Enable Reset Button

        except Exception as e:
            logger.error(f"❌ Error processing file {filename}: {e}")
            return [False, f"❌ Error: {e}", None, True]  # Handle errors gracefully
