import dash_bootstrap_components as dbc
import polars as pl
import logging
from dash import Dash, Input, Output, dash_table, html
from utils.store import Store
from utils.logger_config import logger  # Import the logger


def register_duplicate_rows_callbacks(app: "Dash") -> None:
    """Registers callback to detect and display duplicate rows."""

    @app.callback(
        Output("duplicate-rows", "children"),
        Input("file-upload-status", "data"),
    )
    def render_duplicate_rows(trigger):
        """Displays duplicate row count and a scrollable table of duplicates using `dash_table.DataTable`."""
        if not trigger:
            logger.warning("⚠️ No dataset loaded. Skipping duplicate rows check.")
            return "No dataset loaded."

        df: pl.DataFrame = Store.get_static("data_frame")

        if df is None:
            logger.warning("⚠️ Dataset not found in memory despite file upload.")
            return "No dataset loaded."

        duplicate_mask = df.is_duplicated()
        num_duplicates = duplicate_mask.sum()

        if num_duplicates > 0:
            duplicate_rows = df.filter(duplicate_mask)  # Get duplicate rows
            logger.warning(f"🔁 Found {num_duplicates:,} duplicate rows.")

            return dbc.Card(
                dbc.CardBody(
                    [
                        html.P(f"🔁 {num_duplicates:,} duplicate rows found."),
                        dash_table.DataTable(
                            data=duplicate_rows.to_dicts(),
                            columns=[{"name": col, "id": col} for col in df.columns],
                            style_table={
                                "maxHeight": "400px",
                                "overflowY": "auto",
                            },
                            page_size=10,
                            style_cell={
                                "textAlign": "left",
                                "whiteSpace": "normal",
                            },
                            style_header={
                                "backgroundColor": "lightgrey",
                                "fontWeight": "bold",
                            },
                        ),
                    ]
                ),
                className="shadow-sm",
            )

        logger.info("✅ No duplicate rows found.")
        return html.P("✅ No duplicate rows found.")
