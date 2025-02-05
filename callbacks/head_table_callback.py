import base64
import io

import polars as pl
from dash import Dash, Input, Output, State

from components.table import table_component
from utils.store import Store
from dash import html
import dash


def register_head_table_callbacks(app: "Dash") -> None:

    @app.callback(
        Output("output-table", "children"),
        Input("file-upload-status", "data"),  # Trigger variable
        prevent_initial_call=True,
    )
    def render_table(trigger):
        """Renders the data table when a file is successfully uploaded."""
        if trigger:
            df: pl.DataFrame = Store.get_static("data_frame")
            if df is not None:
                return table_component(df.head(10))

        return "No data available for display."
