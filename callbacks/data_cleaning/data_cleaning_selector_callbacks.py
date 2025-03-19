import polars as pl
from dash import Input, Output, ctx
from utils.logger_config import logger
from utils.store import Store


def register_data_cleaning_selector_callbacks(app) -> None:
    """Registers callbacks for selecting columns in data cleaning page."""

    @app.callback(
        [
            Output("column-select-missing", "options"),
            Output("column-select-outlier", "options"),
            Output("column-select-type", "options"),
            Output("duplicate-columns", "options"),
        ],
        Input("file-upload-status", "data"),
    )
    def update_column_dropdowns(file_uploaded):
        """Populates the dropdowns with available columns."""
        if not file_uploaded:
            logger.warning("⚠️ No file uploaded. Cannot populate column dropdowns.")
            return [], [], [], []

        df: pl.DataFrame = Store.get_static("data_frame")

        if df is None:
            logger.warning(
                "⚠️ No dataset in memory despite file upload. Possible storage issue."
            )
            return [], [], [], []

        # Get column names
        columns = [{"label": col, "value": col} for col in df.columns]

        logger.info("✅ Column dropdowns updated successfully.")
        return columns, columns, columns, columns
