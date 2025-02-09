import logging
import polars as pl
from dash import Input, Output, html, dash_table
import dash_bootstrap_components as dbc
from utils.store import Store
from utils.logger_config import logger
from utils.cache_manager import CACHE_MANAGER


def register_statistic_table_callbacks(app):
    """Registers callbacks for dataset descriptive statistics."""

    @app.callback(
        Output("stats-table", "children"),  # Displays the describe table
        Input("file-upload-status", "data"),  # Triggered when a file is uploaded
    )
    def update_stats_table(file_uploaded):
        """Computes and displays dataset descriptive statistics."""

        if not file_uploaded:
            return "No dataset loaded."

        df: pl.DataFrame = Store.get_static("data_frame")
        if df is None or df.is_empty():
            return "No data available for statistical summary."

        # ✅ Generate a unique cache key based on dataset shape
        cache_key = f"dataset_statistics_{df.shape}"
        cached_stats = CACHE_MANAGER.load_cache(cache_key, df)
        if cached_stats:
            return cached_stats  # ✅ Return cached result instantly

        try:
            logger.info("📊 Computing dataset statistics...")

            # ✅ Compute `.describe()` for statistical summary
            stats_df = df.describe()

            # ✅ Convert `.describe()` output to a Dash DataTable
            stats_table = dash_table.DataTable(
                data=stats_df.to_dicts(),
                columns=[{"name": col, "id": col} for col in stats_df.columns],
                style_table={
                    "maxHeight": "500px",
                    "overflowY": "auto",
                    "overflowX": "auto",
                    "borderRadius": "8px",
                    "boxShadow": "0px 4px 8px rgba(0,0,0,0.1)",
                    "border": "1px solid #dee2e6",
                },
                style_cell={
                    "textAlign": "left",
                    "padding": "8px",
                    "fontSize": "14px",
                    "whiteSpace": "normal",
                },
                style_header={
                    "backgroundColor": "#007bff",
                    "color": "white",
                    "fontWeight": "bold",
                },
                style_data_conditional=[
                    {"if": {"row_index": "odd"}, "backgroundColor": "#f8f9fa"}
                ],
            )

            logger.info("✅ Data summary table successfully generated.")

            # ✅ Store computed summary in cache
            result = stats_table

            CACHE_MANAGER.save_cache(cache_key, df, result)
            logger.info("💾 Cached data summary for future use.")

            return result

        except Exception as e:
            logger.error(f"❌ Error while computing dataset statistics: {e}")
            return "❌ Failed to compute statistics."
