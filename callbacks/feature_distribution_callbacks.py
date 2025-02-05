import polars as pl
import plotly.express as px
from dash import Dash, Input, Output, State, dcc
from utils.store import Store
import plotly.graph_objects as go


def register_feature_distribution_callbacks(app: "Dash") -> None:
    """Registers callbacks for generating feature distribution histograms."""

    @app.callback(
        Output("column-dropdown", "options"),  # Populate dropdown options
        Output("column-dropdown", "value"),  # Set default selected value
        Input("file-upload-status", "data"),  # Trigger when file is uploaded
        # prevent_initial_call=True,
    )
    def update_column_dropdown(file_uploaded):
        """Populates the dropdown with numerical feature names and selects the second column by default."""
        if file_uploaded:
            df: pl.DataFrame = Store.get_static("data_frame")
            if df is not None:
                # Select only numeric columns
                numeric_columns = [
                    col for col in df.columns if df[col].dtype in (pl.Float64, pl.Int64)
                ]

                options = [{"label": col, "value": col} for col in numeric_columns[1::]]

                # Default to second column if available
                default_value = options[0]["value"] if len(options) > 1 else None

                return options, default_value

        return [], None  # Empty dropdown if no data

    @app.callback(
        Output("distribution-plot", "figure"),  # Update histogram plot
        Input("column-dropdown", "value"),  # Selected column for distribution
        State("file-upload-status", "data"),  # Ensure file is uploaded
        prevent_initial_call=True,
    )
    def update_distribution_plot(column_name, file_uploaded):
        """Creates a histogram for the selected feature."""
        if file_uploaded and column_name:
            print(f"Generating distribution plot for {column_name}")
            df: pl.DataFrame = Store.get_static("data_frame")
            if df is not None and column_name in df.columns:
                # Extract column values directly from Polars
                column_data = df[column_name].to_list()  # Convert to a list for Plotly

                # Create histogram using Plotly
                fig = px.histogram(
                    x=column_data,  # Pass raw data
                    nbins=30,
                    title=f"Distribution of {column_name}",
                    labels={"x": column_name, "y": "Count"},
                    template="plotly_white",
                )
                return fig

        return go.Figure()  # Return empty plot if no column is selected
