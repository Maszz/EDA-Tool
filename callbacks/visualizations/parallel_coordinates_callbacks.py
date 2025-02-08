import logging
import polars as pl
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from dash import Input, Output
from utils.store import Store
from utils.logger_config import logger  # Import logger


def register_parallel_coordinates_callbacks(app):
    """Registers the callback for Parallel Coordinates visualization."""

    @app.callback(
        Output("parallel-coordinates", "figure"),
        Input("file-upload-status", "data"),
        Input("multivariate-features-dropdown", "value"),
    )
    def update_parallel_coordinates(file_uploaded, selected_features):
        """Generates a parallel coordinates plot for multivariate relationships."""

        if not file_uploaded:
            logger.warning("⚠️ No dataset uploaded. Clearing parallel coordinates plot.")
            return go.Figure()

        df: pl.DataFrame = Store.get_static("data_frame")

        if df is None:
            logger.error("❌ Dataset not found in memory despite file upload.")
            return go.Figure()

        if not selected_features or not all(
            col in df.columns for col in selected_features
        ):
            logger.warning(
                f"⚠️ Invalid or missing features selected: {selected_features}"
            )
            return go.Figure()

        try:
            # Convert selected features to NumPy array
            data = np.column_stack([df[col].to_numpy() for col in selected_features])

            # Convert back to Polars DataFrame with correct column names
            parallel_df = pl.DataFrame(data, schema=selected_features)

            # Generate Parallel Coordinates Plot
            fig = px.parallel_coordinates(
                parallel_df,
                dimensions=selected_features,
                title="Parallel Coordinates Plot",
                template="plotly_white",
            )

            logger.info(
                f"✅ Successfully generated parallel coordinates plot for features: {selected_features}"
            )
            return fig

        except Exception as e:
            logger.error(f"❌ Error generating parallel coordinates plot: {e}")
            return go.Figure()
