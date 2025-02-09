import polars as pl
from dash import Input, Output, ctx

from utils.logger_config import logger  # Import logger
from utils.store import Store


def register_feature_importance_selector_callbacks(app) -> None:
    """Registers callbacks for selecting target column and updating training status."""

    @app.callback(
        Output("target-column", "options"),  # Populate dropdown options
        Output(
            "training-status", "children", allow_duplicate=True
        ),  # Update training status
        Input("file-upload-status", "data"),  # Trigger when a file is uploaded
        Input("target-column", "value"),  # Trigger when a new target column is selected
        Input("importance-method", "value"),  # Trigger when importance method changes
    )
    def update_target_dropdown(file_uploaded, target_column, importance_method):
        """Populates the dropdown with available columns and updates training status."""
        ctx_id = ctx.triggered_id  # Identify what triggered the callback

        if not file_uploaded:
            logger.warning(
                "⚠️ No file uploaded. Cannot populate target column dropdown."
            )
            return [], "⚠️ No dataset loaded."

        df: pl.DataFrame = Store.get_static("data_frame")

        if df is None:
            logger.warning(
                "⚠️ No dataset in memory despite file upload. Possible storage issue."
            )
            return [], "⚠️ Dataset not found in memory."

        # Get column names (excluding the first column, assuming it's an ID column)
        options = [{"label": col, "value": col} for col in df.columns[1:]]

        # Determine what message to display based on trigger
        if ctx_id == "file-upload-status":
            logger.info("📁 New file uploaded. Awaiting target column selection.")
            return options, "⚠️ No target column selected."

        if ctx_id in ["target-column", "importance-method"]:
            logger.info(
                f"🔄 Target column: {target_column} | Method: {importance_method}. Training in progress."
            )
            return options, "⏳ Training in Progress... Please wait."

        logger.info("✅ Target column dropdown updated successfully.")
        return options, ""  # Default state
