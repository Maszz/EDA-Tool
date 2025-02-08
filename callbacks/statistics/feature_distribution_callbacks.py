import logging
import plotly.express as px
import plotly.graph_objects as go
import polars as pl
from dash import Dash, Input, Output, State
from utils.store import Store
from utils.logger_config import logger  # Import logger


def register_feature_distribution_callbacks(app: "Dash") -> None:
    """Registers callbacks for generating feature distribution histograms."""

    @app.callback(
        Output("distribution-plot", "figure"),  # Update histogram plot
        Input("column-dropdown", "value"),  # Selected column for distribution
        State("file-upload-status", "data"),  # Ensure file is uploaded
    )
    def update_distribution_plot(column_name, file_uploaded):
        """Creates a histogram for the selected feature."""
        if not file_uploaded:
            logger.warning("⚠️ No dataset uploaded. Skipping distribution plot.")
            return go.Figure()

        df: pl.DataFrame = Store.get_static("data_frame")

        if df is None:
            logger.error("❌ Dataset not found in memory despite file upload.")
            return go.Figure()

        if not column_name:
            logger.warning("⚠️ No column selected for distribution plot.")
            return go.Figure()

        if column_name not in df.columns:
            logger.error(f"❌ Column '{column_name}' not found in dataset.")
            return go.Figure()

        logger.info(f"📊 Generating distribution plot for '{column_name}'.")

        try:
            # Extract column values
            column_data = df[column_name].to_list()  # Convert to list for Plotly

            # Create histogram
            fig = px.histogram(
                x=column_data,
                nbins=30,
                title=f"Distribution of {column_name}",
                labels={"x": column_name, "y": "Count"},
                template="plotly_white",
            )

            logger.info(
                f"✅ Successfully generated distribution plot for '{column_name}'."
            )
            return fig

        except Exception as e:
            logger.error(f"❌ Error generating distribution plot: {e}")
            return go.Figure()
