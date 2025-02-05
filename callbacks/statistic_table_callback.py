import base64
import io

import polars as pl
from dash import Dash, Input, Output, State

from components.table import table_component
from utils.store import Store
from dash import html
import dash


def register_stat_table_callbacks(app: "Dash") -> None:

    @app.callback(
        Output("stats-table", "children"),  # Populate the stats table
        Input("file-upload-status", "data"),  # Triggered when a file is uploaded
        # prevent_initial_call=True,
    )
    def update_stats_table(file_uploaded):
        """Compute and display the statistical summary of the dataset."""
        if file_uploaded:
            df: pl.DataFrame = Store.get_static("data_frame")
            if df is not None:
                # Compute statistical summary using Polars
                stats = df.describe()

                # Convert Polars DataFrame to Dict for Dash Table
                return table_component(stats)

        # Default message when no data is available
        return "No data available for statistical summary."
