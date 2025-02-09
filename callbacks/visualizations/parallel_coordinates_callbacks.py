import logging
import polars as pl
import plotly.express as px
import plotly.graph_objects as go
from dash import Input, Output
from utils.store import Store
from utils.logger_config import logger  # Import logger
from utils.cache_manager import CACHE_MANAGER  # Import Cache Manager
from plotly_resampler import FigureResampler  # ✅ Adds resampling for large datasets


def register_parallel_coordinates_callbacks(app):
    """Registers the callback for Parallel Coordinates visualization."""

    @app.callback(
        Output("parallel-coordinates", "figure"),
        Input("file-upload-status", "data"),
        Input("multivariate-features-dropdown", "value"),
    )
    def update_parallel_coordinates(file_uploaded, selected_features):
        """Generates an optimized parallel coordinates plot for multivariate relationships."""

        if not file_uploaded:
            return go.Figure()

        df: pl.DataFrame = Store.get_static("data_frame")
        if df is None or not selected_features:
            return go.Figure()  # No valid data

        # ✅ Filter only valid numerical features
        valid_features = [
            col
            for col in selected_features
            if col in df.columns and df[col].dtype in (pl.Float64, pl.Int64)
        ]

        if len(valid_features) < 2:
            return go.Figure()  # Parallel plot requires at least 2 features

        # ✅ Generate cache key using dataset shape (prevents unnecessary recomputation)
        cache_key = f"parallel_coordinates_{'_'.join(valid_features)}_{df.shape}"
        cached_result = CACHE_MANAGER.load_cache(cache_key, df)
        if cached_result:
            return cached_result  # Return cached result

        try:
            # ✅ Select only necessary columns (keeps data in Polars)
            parallel_df = df.select(
                valid_features
            ).to_dicts()  # Convert to dict for Plotly

            # ✅ Resampled Parallel Coordinates Plot
            fig = FigureResampler(
                px.parallel_coordinates(
                    parallel_df,
                    dimensions=valid_features,
                    title="Resampled Parallel Coordinates Plot",
                    template="plotly_white",
                )
            )

            # ✅ Store in cache
            CACHE_MANAGER.save_cache(cache_key, df, fig)

            return fig

        except Exception as e:
            logger.error(f"❌ Error generating parallel coordinates plot: {e}")
            return go.Figure()
