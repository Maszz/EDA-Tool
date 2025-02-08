import logging
import polars as pl
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from dash import Input, Output
from sklearn.decomposition import PCA
from utils.store import Store
from utils.logger_config import logger  # Import logger
from utils.cache_manager import CACHE_MANAGER  # Import Cache Manager


def register_pca_projection_callbacks(app):
    """Registers the callback for PCA 2D Projection visualization."""

    @app.callback(
        Output("pca-plot", "figure"),
        Input("file-upload-status", "data"),
    )
    def update_pca_plot(file_uploaded):
        """Generates a PCA 2D Projection for feature clustering while handling missing values."""

        if not file_uploaded:
            logger.warning("⚠️ No dataset uploaded. Clearing PCA plot.")
            return go.Figure()

        df: pl.DataFrame = Store.get_static("data_frame")

        if df is None:
            logger.error("❌ Dataset not found in memory despite file upload.")
            return go.Figure()

        # Select numerical columns
        num_cols = [
            col
            for col in df.columns
            if df[col].dtype in [pl.Float64, pl.Float32, pl.Int64, pl.Int32]
        ]

        if len(num_cols) < 2:
            logger.warning(
                "⚠️ PCA requires at least two numerical features. Insufficient data."
            )
            return go.Figure()

        # Generate cache key
        cache_key = "pca_projection"
        cached_result = CACHE_MANAGER.load_cache(cache_key, df)

        if cached_result:
            logger.info(f"✅ Loaded cached PCA 2D projection.")
            return cached_result

        try:
            # Handle missing values: replace NaNs with None & drop them
            clean_df = df.select(num_cols).fill_nan(None).drop_nulls()

            # Ensure we still have enough data for PCA
            if clean_df.is_empty() or clean_df.shape[0] < 2:
                logger.warning(
                    "⚠️ Insufficient data for PCA after cleaning missing values."
                )
                return go.Figure()

            # Convert to NumPy for PCA
            data_matrix = clean_df.to_numpy()

            # Perform PCA
            pca = PCA(n_components=2)
            reduced = pca.fit_transform(data_matrix)

            # Convert PCA results to NumPy for plotting
            pca_x = reduced[:, 0]
            pca_y = reduced[:, 1]

            # Create Plotly Scatter Plot
            fig = px.scatter(
                x=pca_x,
                y=pca_y,
                title="PCA 2D Projection",
                labels={
                    "x": "Principal Component 1",
                    "y": "Principal Component 2",
                },
                template="plotly_white",
            )

            logger.info(
                f"✅ Successfully generated PCA 2D projection with {len(pca_x)} points."
            )

            # Store in cache
            CACHE_MANAGER.save_cache(cache_key, df, fig)

            return fig

        except Exception as e:
            logger.error(f"❌ Error generating PCA plot: {e}")
            return go.Figure()
