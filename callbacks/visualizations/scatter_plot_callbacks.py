import logging
import polars as pl
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from dash import Input, Output
from utils.store import Store
from utils.logger_config import logger  # Import logger
from utils.cache_manager import CACHE_MANAGER  # Import Cache Manager


def register_scatter_plot_callbacks(app):
    """Registers callbacks for the Scatter Plot visualization."""

    @app.callback(
        Output("scatter-plot", "figure"),
        Input("file-upload-status", "data"),
        Input("feature-x-dropdown", "value"),
        Input("feature-y-dropdown", "value"),
    )
    def update_scatter_plot(file_uploaded, feature_x, feature_y):
        """Generates a scatter plot for selected numerical features with caching and error handling."""

        if not file_uploaded:
            logger.warning("⚠️ No dataset uploaded. Clearing Scatter plot.")
            return go.Figure()

        df: pl.DataFrame = Store.get_static("data_frame")

        if df is None:
            logger.error("❌ Dataset not found in memory despite file upload.")
            return go.Figure()

        if not feature_x or not feature_y:
            logger.warning("⚠️ Missing feature selection for Scatter plot.")
            return go.Figure()

        if feature_x not in df.columns or feature_y not in df.columns:
            logger.error(
                f"❌ Selected features {feature_x} or {feature_y} not found in dataset."
            )
            return go.Figure()

        # Generate a cache key for the scatter plot
        cache_key = f"scatter_{feature_x}_{feature_y}"
        cached_plot = CACHE_MANAGER.load_cache(cache_key, df)

        if cached_plot:
            logger.info(
                f"✅ Loaded cached Scatter plot for {feature_x} vs {feature_y}."
            )
            return cached_plot

        try:
            # Extract feature data
            x_data = df[feature_x].drop_nulls().to_numpy()
            y_data = df[feature_y].drop_nulls().to_numpy()

            # Ensure sufficient data points
            if x_data.size == 0 or y_data.size == 0:
                logger.warning("⚠️ Insufficient valid data points for Scatter plot.")
                return go.Figure()

            fig = px.scatter(
                x=x_data,
                y=y_data,
                title=f"Scatter Plot: {feature_x} vs {feature_y}",
                labels={"x": feature_x, "y": feature_y},
                template="plotly_white",
            )

            logger.info(
                f"✅ Successfully generated Scatter plot for {feature_x} vs {feature_y}."
            )

            # Store the generated plot in cache
            CACHE_MANAGER.save_cache(cache_key, df, fig)

            return fig

        except Exception as e:
            logger.error(f"❌ Error generating Scatter plot: {e}")
            return go.Figure()
