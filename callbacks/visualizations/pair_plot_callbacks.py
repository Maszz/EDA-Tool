import logging
import polars as pl
import plotly.express as px
import plotly.graph_objects as go
from dash import Input, Output
from utils.store import Store
from utils.logger_config import logger  # Import logger
from utils.cache_manager import CACHE_MANAGER  # Import Cache Manager
from plotly_resampler import FigureResampler  # ✅ Adds resampling for large datasets


def register_pair_plot_callbacks(app):
    """Registers callbacks for the Pair Plot visualization."""

    @app.callback(
        Output("pair-plot", "figure"),
        Input("file-upload-status", "data"),
        Input("pairplot-features-dropdown", "value"),
    )
    def update_pair_plot(file_uploaded, selected_features):
        """Generates a resampled pair plot for selected numerical features using Polars."""

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
            return go.Figure()  # Pair plot requires at least 2 features

        # ✅ Generate cache key using dataset shape (prevents unnecessary recomputation)
        cache_key = f"pair_plot_{'_'.join(valid_features)}_{df.shape}"
        cached_result = CACHE_MANAGER.load_cache(cache_key, df)
        if cached_result:
            return cached_result  # Return cached result

        try:
            # ✅ Select only necessary columns (keeps data in Polars)
            pairplot_df = df.select(valid_features).to_dicts()  # Convert to dict

            # ✅ Resampled Pair Plot
            fig = FigureResampler(
                px.scatter_matrix(
                    pairplot_df,  # Use dictionary-based input
                    dimensions=valid_features,
                    title="Resampled Pair Plot of Selected Features",
                    template="plotly_white",
                )
            )

            # ✅ Store in cache
            CACHE_MANAGER.save_cache(cache_key, df, fig)

            return fig

        except Exception as e:
            logger.error(f"❌ Error generating resampled pair plot: {e}")
            return go.Figure()
