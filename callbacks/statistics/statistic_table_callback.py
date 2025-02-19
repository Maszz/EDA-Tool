import polars as pl
from dash import Input, Output, dash_table
from utils.cache_manager import CACHE_MANAGER
from utils.logger_config import logger
from utils.store import Store


def register_statistic_table_callbacks(app) -> None:
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
        cache_key = "dataset_statistics"
        cached_stats = CACHE_MANAGER.load_cache(
            cache_key,
            df,
        )
        if cached_stats:
            data, columns = cached_stats
        else:
            try:
                logger.info("📊 Computing dataset statistics...")
                stats_df = df.describe()
                data, columns = stats_df.to_dicts(), stats_df.columns
                CACHE_MANAGER.save_cache(
                    cache_key,
                    df,
                    (data, columns),
                )
                logger.info("💾 Cached data summary for future use.")
            except Exception as e:
                logger.error(f"❌ Error while computing dataset statistics: {e}")
                return "❌ Failed to compute statistics."

        return dash_table.DataTable(
            data=data,
            columns=[{"name": col, "id": col} for col in columns],
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
