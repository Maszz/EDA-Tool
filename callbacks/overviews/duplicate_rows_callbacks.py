import dash_bootstrap_components as dbc
import polars as pl
from dash import Dash, Input, Output, dash_table, html

from utils.cache_manager import CACHE_MANAGER  # Import the cache manager
from utils.logger_config import logger  # Import the logger
from utils.store import Store


def generate_duplicate_table(data, columns, title, highlight_color="#007bff"):
    """Generates a Dash DataTable wrapped inside a Bootstrap Card."""
    table = (
        dash_table.DataTable(
            data=data,
            columns=[{"name": col, "id": col} for col in columns],
            style_table={
                "maxHeight": "400px",
                "overflowY": "auto",
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


def register_duplicate_rows_callbacks(app: "Dash") -> None:
    """Registers callback to detect and display duplicate rows."""

    @app.callback(
        Output("duplicate-rows", "children"),
        Input("file-upload-status", "data"),
    )
    def render_duplicate_rows(trigger):
        if not trigger:
            return "No dataset loaded."

        df: pl.DataFrame = Store.get_static("data_frame")
        if df is None:
            return "No dataset loaded."

        cache_key = "duplicate_rows"
        cached_result = CACHE_MANAGER.load_cache(cache_key, df)
        if cached_result:

            num_duplicates, data = cached_result
            return (
                generate_duplicate_table(
                    data,
                    df.columns,
                    f"🔁 {num_duplicates:,} Duplicate Rows Found",
                    "#dc3545",
                )
                if num_duplicates > 0
                else html.P("✅ No duplicate rows found.")
            )

        duplicate_mask = df.is_duplicated()
        num_duplicates = duplicate_mask.sum()

        if num_duplicates > 0:
            duplicate_rows = df.filter(duplicate_mask)
            logger.warning(f"🔁 Found {num_duplicates:,} duplicate rows.")
            data = duplicate_rows.to_dicts()
            CACHE_MANAGER.save_cache(cache_key, df, (num_duplicates, data))
            return generate_duplicate_table(
                data,
                df.columns,
                f"🔁 {num_duplicates:,} Duplicate Rows Found",
                "#dc3545",
            )

        logger.info("✅ No duplicate rows found.")
        return html.P("✅ No duplicate rows found.")
