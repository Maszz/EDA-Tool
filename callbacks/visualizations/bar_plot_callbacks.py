import logging
import polars as pl
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from dash import Input, Output
from utils.store import Store
from utils.logger_config import logger  # Import logger
from utils.cache_manager import CACHE_MANAGER  # Import Cache Manager


def register_bar_plot_callbacks(app):
    """Registers callbacks for the Bar Plot visualization."""

    @app.callback(
        Output("bar-plot", "figure"),
        Input("file-upload-status", "data"),
        Input("categorical-dropdown", "value"),
    )
    def update_bar_plot(file_uploaded, selected_categorical):
        """Generates a bar plot for categorical feature distribution."""

        if not file_uploaded:
            logger.warning("⚠️ No dataset uploaded. Clearing bar plot.")
            return go.Figure()

        df: pl.DataFrame = Store.get_static("data_frame")

        if df is None:
            logger.error("❌ Dataset not found in memory despite file upload.")
            return go.Figure()

        if not selected_categorical or selected_categorical not in df.columns:
            logger.warning(
                f"⚠️ Selected column '{selected_categorical}' is missing or invalid."
            )
            return go.Figure()

        # Generate cache key
        cache_key = f"bar_plot_{selected_categorical}"
        cached_result = CACHE_MANAGER.load_cache(cache_key, df)

        if cached_result:
            logger.info(f"✅ Loaded cached bar plot for '{selected_categorical}'.")
            return cached_result

        try:
            # Extract unique values and counts
            unique_values, counts = np.unique(
                df[selected_categorical].to_numpy(), return_counts=True
            )

            if unique_values.size == 0:
                logger.warning(f"⚠️ No data found for column '{selected_categorical}'.")
                return go.Figure()

            # Create bar plot
            fig_bar = px.bar(
                x=unique_values,
                y=counts,
                title=f"Bar Plot: {selected_categorical}",
                labels={"x": selected_categorical, "y": "Count"},
                template="plotly_white",
            )

            logger.info(
                f"✅ Successfully generated bar plot for '{selected_categorical}'."
            )

            # Store in cache
            CACHE_MANAGER.save_cache(cache_key, df, fig_bar)

            return fig_bar

        except Exception as e:
            logger.error(
                f"❌ Error generating bar plot for '{selected_categorical}': {e}"
            )
            return go.Figure()
