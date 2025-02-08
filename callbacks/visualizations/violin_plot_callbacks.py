import logging
import polars as pl
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from dash import Input, Output
from utils.store import Store
from utils.logger_config import logger  # Import logger
from utils.cache_manager import CACHE_MANAGER  # Import Cache Manager


def register_violin_plot_callbacks(app):
    """Registers callbacks for the Violin Plot visualization with caching."""

    @app.callback(
        Output("violin-plot", "figure"),
        Input("file-upload-status", "data"),
        Input("categorical-dropdown", "value"),
        Input("numeric-dropdown", "value"),
    )
    def update_violin_plot(file_uploaded, categorical_feature, numerical_feature):
        """Generates a violin plot for a numerical feature grouped by a categorical feature with caching and error handling."""

        if not file_uploaded:
            return _log_and_return_empty("⚠️ No dataset uploaded. Clearing Violin plot.")

        df: pl.DataFrame = Store.get_static("data_frame")

        if df is None:
            return _log_and_return_empty(
                "❌ Dataset not found in memory despite file upload."
            )

        if not categorical_feature or not numerical_feature:
            return _log_and_return_empty("⚠️ Missing feature selection for Violin plot.")

        if categorical_feature not in df.columns or numerical_feature not in df.columns:
            return _log_and_return_empty(
                f"❌ Selected features {categorical_feature} or {numerical_feature} not found in dataset."
            )

        # Generate a cache key based on dataset hash and selected features
        cache_key = f"violin_{categorical_feature}_{numerical_feature}"
        cached_plot = CACHE_MANAGER.load_cache(cache_key, df)

        if cached_plot:
            logger.info(
                f"✅ Loaded cached Violin plot for {numerical_feature} by {categorical_feature}."
            )
            return cached_plot

        try:
            # Extract selected features and drop missing values
            clean_df = df.select([categorical_feature, numerical_feature]).drop_nulls()

            # Ensure sufficient data points
            if clean_df.height < 2:
                return _log_and_return_empty(
                    "⚠️ Insufficient valid data points for Violin plot."
                )

            # Convert Polars DataFrame to dictionary format for Plotly
            fig = px.violin(
                clean_df.to_dicts(),
                x=categorical_feature,
                y=numerical_feature,
                box=True,
                points="all",
                title=f"Violin Plot: {numerical_feature} by {categorical_feature}",
                labels={
                    categorical_feature: "Category",
                    numerical_feature: "Value",
                },
                template="plotly_white",
            )

            logger.info(
                f"✅ Successfully generated Violin plot for {numerical_feature} grouped by {categorical_feature}."
            )

            # Store the generated plot in cache
            CACHE_MANAGER.save_cache(cache_key, df, fig)

            return fig

        except Exception as e:
            logger.error(f"❌ Error generating Violin plot: {e}")
            return go.Figure()


def _log_and_return_empty(message: str):
    """Helper function to log a warning and return an empty figure."""
    logger.warning(message)
    return go.Figure()
