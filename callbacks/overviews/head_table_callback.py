import dash_bootstrap_components as dbc
import polars as pl
from dash import Dash, Input, Output, dash_table, html

from utils.cache_manager import CACHE_MANAGER  # Import cache manager
from utils.logger_config import logger  # Import logger
from utils.store import Store


def generate_head_table(data, columns, title, highlight_color="#007bff"):
    """Generates a Dash DataTable wrapped inside a Bootstrap Card."""
    table = (
        dash_table.DataTable(
            data=data,
            columns=[{"name": col, "id": col} for col in columns],
            style_table={
                "maxHeight": "400px",
                "overflowY": "auto",
                "overflowX": "auto",
                "borderRadius": "8px",
                "boxShadow": "0px 4px 8px rgba(0,0,0,0.1)",
                "border": "1px solid #dee2e6",
            },
            page_size=10,
            virtualization=True,
            style_cell={
                "textAlign": "left",
                "padding": "8px",
                "fontSize": "14px",
                "whiteSpace": "normal",
            },
            style_header={
                "backgroundColor": highlight_color,
                "color": "white",
                "fontWeight": "bold",
            },
            style_data_conditional=[
                {"if": {"row_index": "odd"}, "backgroundColor": "#f8f9fa"}
            ],
        )
        if data
        else html.P("✅ No relevant data found.")
    )

    return dbc.Card(
        dbc.CardBody(
            [
                html.H5(title, className="card-title"),
                table,
            ]
        ),
        className="shadow-sm",
    )


def register_head_table_callbacks(app: "Dash") -> None:
    """Registers callback to display the first 10 rows of the dataset in a table."""

    @app.callback(
        Output("output-table", "children"),
        Input("file-upload-status", "data"),
    )
    def render_table(trigger):
        if not trigger:
            return "No data available for display."

        df: pl.DataFrame = Store.get_static("data_frame")
        if df is None or df.is_empty():
            return "No data available for display."

        cache_key = "head_table"
        cached_result = CACHE_MANAGER.load_cache(cache_key, df)
        if cached_result:
            return generate_head_table(
                cached_result, df.columns, "📋 First 10 Rows of Dataset"
            )

        logger.info(
            f"📋 Displaying first 10 rows of dataset ({df.shape[0]} rows, {df.shape[1]} columns)."
        )
        data = df.head(10).to_dicts()
        CACHE_MANAGER.save_cache(cache_key, df, data)

        return generate_head_table(data, df.columns, "📋 First 10 Rows of Dataset")
