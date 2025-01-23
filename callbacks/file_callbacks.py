import base64
import io

import pandas as pd
import polars as pl
from dash import Dash, Input, Output, State

from components.table import table_component
from utils.store import Store


def register_file_callbacks(app: "Dash") -> None:
    """Define callbacks for file handling."""

    @app.callback(
        Output("output-table", "children"),
        Input("file-upload", "contents"),
        State("file-upload", "filename"),
    )
    def update_output(contents: str, filename: str) -> str:
        if contents is not None:
            content_type, content_string = contents.split(",")
            decoded = base64.b64decode(content_string)

            try:
                # Read file into DataFrame
                if filename.endswith(".csv"):
                    # df = pd.read_csv(io.StringIO(decoded.decode("utf-8")))
                    df = pl.read_csv(io.StringIO(decoded.decode("utf-8")))
                    Store.set_static("data_frame", df)
                elif filename.endswith(".xlsx"):
                    df = pd.read_excel(io.BytesIO(decoded))
                else:
                    return "Unsupported file type."

                # Return a DataTable
                return table_component(Store.get_static("data_frame"))

            except Exception as e:
                return f"Error: {e!s}"

        return "No file uploaded yet."

    @app.callback(
        Output("output-table", "children", allow_duplicate=True),
        Input("reset-button", "n_clicks"),
    )
    def reset_button(n_clicks: int) -> str:
        if n_clicks > 0:
            Store.set_static("data_frame", None)
            return "No file uploaded yet."

        return "No file uploaded yet."
