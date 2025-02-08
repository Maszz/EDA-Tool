import polars as pl
import logging
from dash import Dash, Input, Output, html
from utils.store import Store
from utils.logger_config import logger  # Import the logger


def register_file_summary_callbacks(app: "Dash") -> None:
    """Registers callback to display dataset summary (number of rows and columns)."""

    @app.callback(
        Output("file-summary", "children"),
        Input("file-upload-status", "data"),
    )
    def render_file_summary(trigger):
        """Displays dataset shape: number of rows and columns."""
        if not trigger:
            logger.warning("⚠️ No dataset loaded. Skipping file summary.")
            return "No dataset loaded."

        df: pl.DataFrame = Store.get_static("data_frame")

        if df is None:
            logger.warning("⚠️ Dataset not found in memory despite file upload.")
            return "No dataset loaded."

        num_rows, num_cols = df.shape
        logger.info(f"📊 Dataset Summary: {num_rows:,} rows, {num_cols:,} columns.")
        return html.P(f"📊 {num_rows:,} rows, {num_cols:,} columns")
