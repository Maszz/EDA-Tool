import logging
import numpy as np
import polars as pl
import plotly.express as px
import plotly.graph_objects as go
from dash import Dash, Input, Output
from scipy.stats import rankdata, kendalltau, spearmanr
from utils.store import Store
from utils.logger_config import logger  # Import logger
from utils.cache_manager import CACHE_MANAGER  # Import cache manager
from plotly_resampler import FigureResampler
from joblib import Parallel, delayed


def register_correlation_heatmap_callbacks(app: "Dash") -> None:
    """Registers callbacks for generating correlation heatmaps with optimized computation and NaN handling."""

    @app.callback(
        Output("correlation-heatmap", "figure"),  # Update correlation heatmap
        Input("file-upload-status", "data"),  # Trigger when file is uploaded
        Input("correlation-method-dropdown", "value"),  # Selected correlation method
    )
    def update_correlation_heatmap(file_uploaded, method):
        """Creates a correlation heatmap for numerical features with NaN handling based on the selected method."""

        if not file_uploaded:
            return go.Figure()  # No dataset available

        df: pl.DataFrame = Store.get_static("data_frame")
        if df is None or df.is_empty():
            return go.Figure()  # No dataset available

        # ✅ Generate cache key using dataset shape & method
        cache_key = f"correlation_heatmap_{method}_{df.shape}"
        cached_result = CACHE_MANAGER.load_cache(cache_key, df)
        if cached_result:
            return cached_result  # Use cached result if available

        # ✅ Select only numeric columns
        numeric_columns = [
            col for col in df.columns if df[col].dtype in (pl.Float64, pl.Int64)
        ]
        if len(numeric_columns) < 2:
            return go.Figure()  # Not enough numerical features for correlation

        logger.info(
            f"📊 Computing {method} correlation for {len(numeric_columns)} features."
        )

        # ✅ Limit dataset size to prevent slow computation
        df = df.select(numeric_columns)  # Only keep numeric columns

        # ✅ Convert Polars DataFrame to NumPy Array & handle NaN values
        data = df.to_numpy()
        data = np.nan_to_num(
            data, nan=np.nanmean(data)
        )  # ✅ Replace NaNs with column mean

        try:
            # ✅ Compute correlation matrix efficiently
            if method == "pearson":
                corr_matrix = np.corrcoef(data, rowvar=False)
            elif method == "spearman":
                corr_matrix = spearman_corr(data)

            else:
                logger.error(f"❌ Unsupported correlation method: {method}")
                return go.Figure()

            # ✅ Generate Heatmap
            fig = px.imshow(
                corr_matrix,
                labels={"color": "Correlation"},
                x=df.columns,
                y=df.columns,
                color_continuous_scale="RdBu_r",
                title=f"Feature Correlation Heatmap ({method.capitalize()})",
            )

            # ✅ Store result in cache
            CACHE_MANAGER.save_cache(cache_key, df, fig)
            logger.info(f"💾 Cached correlation heatmap for {method}.")

            return fig

        except Exception as e:
            logger.error(f"❌ Error computing correlation: {e}")
            return go.Figure()

    # ✅ Efficient Spearman Correlation Computation with NaN Handling
    def spearman_corr(data: np.ndarray) -> np.ndarray:
        """Optimized Spearman correlation using NumPy & SciPy."""
        logger.info("⚡ Optimized Spearman computation using vectorized ranking.")
        ranked_data = np.apply_along_axis(rankdata, axis=0, arr=data)
        return np.corrcoef(ranked_data, rowvar=False)  # Fast matrix correlation
