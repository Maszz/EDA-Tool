import dash_bootstrap_components as dbc
import polars as pl
from dash import Dash, Input, Output, dash_table

from utils.cache_manager import CACHE_MANAGER  # Import cache manager
from utils.logger_config import logger  # Import logger
from utils.store import Store


def register_head_table_callbacks(app: "Dash") -> None:
    """Registers callback to display the first 10 rows of the dataset in a table."""

    @app.callback(
        Output("output-table", "children"),
        Input("file-upload-status", "data"),
    )
    def render_table(trigger):
        """Displays the first 10 rows of the dataset in a scrollable table."""
        if not trigger:
            return "No data available for display."

        df: pl.DataFrame = Store.get_static("data_frame")

        if df is None or df.is_empty():
            return "No data available for display."

        # ✅ Generate cache key using dataset shape
        cache_key = f"head_table"
        cached_result = CACHE_MANAGER.load_cache(cache_key, df)
        if cached_result:
            return cached_result  # Use cached result if available

        logger.info(
            f"📋 Displaying first 10 rows of dataset ({df.shape[0]} rows, {df.shape[1]} columns)."
        )

        # ✅ Create Styled Table
        result = dbc.Card(
            dbc.CardBody(
                dash_table.DataTable(
                    data=df.head(10).to_dicts(),
                    columns=[{"name": col, "id": col} for col in df.columns],
                    page_size=10,
                    virtualization=True,
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
            ),
            className="shadow-sm",
        )

        # ✅ Store result in cache
        CACHE_MANAGER.save_cache(cache_key, df, result)

        return result
