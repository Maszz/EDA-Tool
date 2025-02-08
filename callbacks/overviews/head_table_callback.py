import logging
import dash_bootstrap_components as dbc
import polars as pl
from dash import Dash, Input, Output, dash_table, html
from utils.store import Store
from utils.logger_config import logger  # Import logger


def register_head_table_callbacks(app: "Dash") -> None:
    """Registers callback to display the first 10 rows of the dataset in a table."""

    @app.callback(
        Output("output-table", "children"),
        Input("file-upload-status", "data"),
    )
    def render_table(trigger):
        """Displays the first 10 rows of the dataset in a scrollable table."""
        if not trigger:
            logger.warning("⚠️ No dataset loaded. Skipping table rendering.")
            return "No data available for display."

        df: pl.DataFrame = Store.get_static("data_frame")

        if df is None:
            logger.warning("⚠️ Dataset not found in memory despite file upload.")
            return "No data available for display."

        logger.info(
            f"📋 Displaying first 10 rows of dataset ({df.shape[0]} rows, {df.shape[1]} columns)."
        )

        return dbc.Card(
            dbc.CardBody(
                dash_table.DataTable(
                    data=df.head(10).to_dicts(),
                    columns=[{"name": col, "id": col} for col in df.columns],
                    style_table={"maxHeight": "400px", "overflowY": "auto"},
                    page_size=10,
                    style_cell={"textAlign": "left", "whiteSpace": "normal"},
                    style_header={
                        "backgroundColor": "lightgrey",
                        "fontWeight": "bold",
                    },
                )
            ),
            className="shadow-sm",
        )
