import polars as pl
from dash import Dash, Input, Output, html

from utils.cache_manager import CACHE_MANAGER  # Import cache manager
from utils.logger_config import logger  # Import the logger
from utils.store import Store


def register_file_summary_callbacks(app: "Dash") -> None:
    """Registers callback to display dataset summary (number of rows and columns)."""

    @app.callback(
        Output("file-summary", "children"),
        Input("file-upload-status", "data"),
    )
    def render_file_summary(trigger):
        """Displays dataset shape: number of rows and columns with caching."""
        if not trigger:
            logger.warning("⚠️ No dataset loaded. Skipping file summary.")
            return "No dataset loaded."

        df: pl.DataFrame = Store.get_static("data_frame")

        if df is None:
            logger.warning("⚠️ Dataset not found in memory despite file upload.")
            return "No dataset loaded."

        # ✅ Check cache before recalculating
        cache_key = "file_summary"
        cached_result = CACHE_MANAGER.load_cache(cache_key, df)
        if cached_result:
            logger.info("🔄 Loaded cached dataset summary.")
            return cached_result  # Return cached result instantly

        # Compute dataset summary
        num_rows, num_cols = df.shape
        logger.info(f"📊 Dataset Summary: {num_rows:,} rows, {num_cols:,} columns.")

        result = html.P(f"📊 {num_rows:,} rows, {num_cols:,} columns")

        # ✅ Store result in cache
        CACHE_MANAGER.save_cache(cache_key, df, result)
        logger.info("💾 Cached dataset summary for future use.")

        return result
