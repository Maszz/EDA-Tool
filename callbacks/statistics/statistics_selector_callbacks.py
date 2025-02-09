import polars as pl
from dash import Input, Output

from utils.logger_config import logger  # Import logger
from utils.store import Store


def register_statistics_selector_callbacks(app) -> None:
    """Registers callbacks for updating user selection components in the Statistics tab."""

    @app.callback(
        [
            Output("column-dropdown", "options"),  # Populate selector options
            Output("column-dropdown", "value"),  # Set default selected value
        ],
        Input("file-upload-status", "data"),  # Trigger when a file is uploaded
    )
    def update_statistics_selector(file_uploaded):
        """Updates the selector with numerical feature names and sets the second column as default."""
        if not file_uploaded:
            logger.warning(
                "⚠️ No dataset uploaded. Clearing statistics selector options."
            )
            return [], None

        df: pl.DataFrame = Store.get_static("data_frame")

        if df is None:
            logger.error("❌ Dataset not found in memory despite file upload.")
            return [], None

        # Select only numeric columns
        numeric_columns = [
            col for col in df.columns if df[col].dtype in (pl.Float64, pl.Int64)
        ]

        if not numeric_columns:
            logger.warning("⚠️ No numerical columns found in dataset.")
            return [], None

        options = [{"label": col, "value": col} for col in numeric_columns]

        # Default to second column if available, otherwise first column
        default_value = (
            (options[1]["value"] if len(options) > 1 else options[0]["value"])
            if options
            else None
        )

        logger.info(
            f"✅ Updated statistics selector with {len(options)} numerical columns. Default: {default_value}"
        )

        return options, default_value
