import dash_bootstrap_components as dbc
import polars as pl
import logging
from dash import Dash, Input, Output, dash_table, html
from utils.store import Store
from utils.logger_config import logger  # Import the logger
from utils.cache_manager import CACHE_MANAGER  # Import the cache manager


def register_data_summary_callbacks(app: "Dash") -> None:
    """Registers callbacks for missing values and data types summary."""

    @app.callback(
        Output("data-summary", "children"),
        Input("file-upload-status", "data"),
    )
    def render_data_summary(trigger):
        """Displays column data types and missing values using Polars with caching."""
        if not trigger:
            logger.warning("⚠️ No dataset loaded. Skipping data summary rendering.")
            return "No dataset loaded."

        df: pl.DataFrame = Store.get_static("data_frame")

        if df is None:
            logger.warning("⚠️ Dataset not found in memory despite file upload.")
            return "No dataset loaded."

        # ✅ Check if data summary is cached
        cache_key = "data_summary"
        cached_result = CACHE_MANAGER.load_cache(cache_key, df)
        if cached_result:
            logger.info("🔄 Loaded cached data summary.")
            return cached_result  # Use cached result instead of recalculating

        # Compute data summary
        total_rows = df.height  # Total number of rows
        summary = df.schema  # Column names and data types
        missing_values = df.null_count()  # Returns a Polars DataFrame

        # Convert missing value counts to dictionary (column name -> missing count)
        missing_dict = {col: missing_values[col][0] for col in df.columns}

        logger.info(f"📊 Data Summary: {len(summary)} columns, {total_rows} rows.")
        logger.info(
            f"⚠️ Missing Values: {sum(missing_dict.values())} total missing entries."
        )

        # Format Data Summary Table
        summary_table = dash_table.DataTable(
            data=[
                {"Column": col, "Type": str(dtype)} for col, dtype in summary.items()
            ],
            columns=[
                {"name": "Column", "id": "Column"},
                {"name": "Type", "id": "Type"},
            ],
            style_table={"maxHeight": "300px", "overflowY": "auto"},
            page_size=10,
            style_cell={"textAlign": "left", "whiteSpace": "normal"},
            style_header={"backgroundColor": "lightgrey", "fontWeight": "bold"},
        )

        # Format Missing Values Table
        missing_table = dash_table.DataTable(
            data=[
                {
                    "Column": col,
                    "Missing Count": missing_count,
                    "Missing %": f"{(missing_count / total_rows * 100):.2f}%",
                }
                for col, missing_count in missing_dict.items()
                if missing_count > 0
            ],
            columns=[
                {"name": "Column", "id": "Column"},
                {"name": "Missing Count", "id": "Missing Count"},
                {"name": "Missing %", "id": "Missing %"},
            ],
            style_table={"maxHeight": "300px", "overflowY": "auto"},
            page_size=10,
            style_cell={"textAlign": "left", "whiteSpace": "normal"},
            style_header={"backgroundColor": "lightgrey", "fontWeight": "bold"},
        )

        logger.info("✅ Data summary table successfully generated.")

        # ✅ Store computed summary in cache
        result = dbc.Card(
            dbc.CardBody(
                [
                    html.H5("📌 Column Data Types", className="card-title"),
                    summary_table,
                    html.Hr(),
                    html.H5("⚠️ Missing Values", className="card-title"),
                    (
                        missing_table
                        if sum(missing_dict.values()) > 0
                        else html.P("✅ No missing values.")
                    ),
                ]
            ),
            className="shadow-sm",
        )

        CACHE_MANAGER.save_cache(cache_key, df, result)
        logger.info("💾 Cached data summary for future use.")

        return result
