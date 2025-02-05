import polars as pl
from dash import Dash, Input, Output
from components.table import table_component
from utils.store import Store


def register_missing_values_callbacks(app: "Dash") -> None:
    """Registers callbacks for missing values and data types summary."""

    @app.callback(
        Output("data-summary", "children"),  # Populate the dataset summary table
        Input("file-upload-status", "data"),  # Triggered when a file is uploaded
        # prevent_initial_call=True,
    )
    def update_data_summary(file_uploaded):
        """Computes and displays the dataset summary including missing values."""
        if file_uploaded:
            df: pl.DataFrame = Store.get_static("data_frame")
            if df is not None:
                # Compute column data types and missing value statistics
                summary_df = pl.DataFrame(
                    {
                        "Feature": df.columns,
                        "Data Type": [str(df[col].dtype) for col in df.columns],
                        "Missing Values": [
                            df[col].is_null().sum() for col in df.columns
                        ],
                        "Missing %": [
                            (df[col].is_null().sum() / df.height * 100)
                            for col in df.columns
                        ],
                    }
                )

                return table_component(summary_df)  # Use the beautified table component

        # Default message when no data is available
        return "No dataset summary available."
