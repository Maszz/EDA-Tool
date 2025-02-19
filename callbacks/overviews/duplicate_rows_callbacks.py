import dash_bootstrap_components as dbc
import polars as pl
from dash import Dash, Input, Output, dash_table, html

from utils.cache_manager import CACHE_MANAGER  # Import the cache manager
from utils.logger_config import logger  # Import the logger
from utils.store import Store


def register_duplicate_rows_callbacks(app: "Dash") -> None:
    """Registers callback to detect and display duplicate rows."""

    @app.callback(
        Output("duplicate-rows", "children"),
        Input("file-upload-status", "data"),
    )
    def render_duplicate_rows(trigger):
        """Displays duplicate row count and a scrollable table of duplicates using caching."""
        if not trigger:
            return "No dataset loaded."

        df: pl.DataFrame = Store.get_static("data_frame")
        if df is None:
            return "No dataset loaded."

        # ✅ Generate cache key using dataset shape
        cache_key = f"duplicate_rows"
        cached_result = CACHE_MANAGER.load_cache(cache_key, df)
        if cached_result:
            return cached_result  # Use cached result instead of recalculating

        # ✅ Compute duplicate rows efficiently
        duplicate_mask = df.is_duplicated()
        num_duplicates = duplicate_mask.sum()

        if num_duplicates > 0:
            duplicate_rows = df.filter(
                duplicate_mask
            )  # ✅ Get duplicate rows efficiently
            logger.warning(f"🔁 Found {num_duplicates:,} duplicate rows.")

            result = dbc.Card(
                dbc.CardBody(
                    [
                        html.H5(
                            f"🔁 {num_duplicates:,} Duplicate Rows Found",
                            className="card-title",
                        ),
                        dash_table.DataTable(
                            data=duplicate_rows.to_dicts(),
                            columns=[{"name": col, "id": col} for col in df.columns],
                            page_size=10,
                            virtualization=True,
                            style_table={
                                "maxHeight": "400px",
                                "overflowY": "auto",
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
                                "backgroundColor": "#dc3545",
                                "color": "white",
                                "fontWeight": "bold",
                            },
                            style_data_conditional=[
                                {
                                    "if": {"row_index": "odd"},
                                    "backgroundColor": "#f8f9fa",
                                }
                            ],
                        ),
                    ]
                ),
                className="shadow-sm",
            )

            # ✅ Store result in cache
            CACHE_MANAGER.save_cache(cache_key, df, result)
            logger.info("💾 Cached duplicate row results for future use.")

            return result

        logger.info("✅ No duplicate rows found.")
        result = html.P("✅ No duplicate rows found.")

        # ✅ Store "no duplicates found" in cache as well
        CACHE_MANAGER.save_cache(cache_key, df, result)

        return result
