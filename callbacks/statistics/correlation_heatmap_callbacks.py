import logging
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
import polars as pl
from dash import Dash, Input, Output
from utils.store import Store
from utils.logger_config import logger  # Import logger
from utils.cache_manager import CACHE_MANAGER


def register_correlation_heatmap_callbacks(app: "Dash") -> None:
    """Registers callbacks for generating correlation heatmaps without Pandas."""

    @app.callback(
        Output("correlation-heatmap", "figure"),  # Update correlation heatmap
        Input("file-upload-status", "data"),  # Trigger when file is uploaded
        Input("correlation-method-dropdown", "value"),  # Selected correlation method
    )
    def update_correlation_heatmap(file_uploaded, method):
        """Creates a correlation heatmap for numerical features based on the selected method."""

        if not file_uploaded:
            logger.warning("⚠️ No dataset uploaded. Skipping correlation heatmap.")
            return go.Figure()

        df: pl.DataFrame = Store.get_static("data_frame")

        if df is None:
            logger.error("❌ Dataset not found in memory despite file upload.")
            return go.Figure()

        # ✅ Check cache before recalculating
        cache_key = f"correlation_heatmap_{method}"
        cached_result = CACHE_MANAGER.load_cache(cache_key, df)
        if cached_result:
            logger.info(f"🔄 Loaded cached correlation heatmap ({method}).")
            return cached_result  # Return cached result instantly

        # Select only numeric columns
        numeric_columns = [
            col for col in df.columns if df[col].dtype in (pl.Float64, pl.Int64)
        ]

        if len(numeric_columns) < 2:
            logger.warning("⚠️ Not enough numerical features to compute correlation.")
            return go.Figure()

        logger.info(
            f"📊 Computing {method} correlation heatmap for {len(numeric_columns)} features."
        )

        # Convert Polars DataFrame to NumPy Array
        data = df.select(numeric_columns).to_numpy()

        try:
            if method == "pearson":
                corr_matrix = np.corrcoef(data, rowvar=False)
            elif method == "spearman":
                corr_matrix = spearman_corr(data)
            elif method == "kendall":
                corr_matrix = kendall_corr(data)
            else:
                logger.error(f"❌ Unsupported correlation method: {method}")
                return go.Figure()

            # Create heatmap
            fig = px.imshow(
                corr_matrix,
                labels={"color": "Correlation"},
                x=numeric_columns,
                y=numeric_columns,
                color_continuous_scale="RdBu_r",
                title=f"Feature Correlation Heatmap ({method.capitalize()})",
            )

            logger.info(
                f"✅ Correlation heatmap generated successfully using {method}."
            )

            # ✅ Store result in cache
            CACHE_MANAGER.save_cache(cache_key, df, fig)
            logger.info(f"💾 Cached correlation heatmap for method {method}.")

            return fig

        except Exception as e:
            logger.error(f"❌ Error computing correlation: {e}")
            return go.Figure()

    # Helper functions for correlation computation
    def spearman_corr(data: np.ndarray) -> np.ndarray:
        """Calculate Spearman correlation matrix using NumPy."""
        logger.info("🔍 Computing Spearman correlation.")
        ranked_data = np.apply_along_axis(rank_data, axis=0, arr=data)
        return np.corrcoef(ranked_data, rowvar=False)

    def rank_data(column: np.ndarray) -> np.ndarray:
        """Compute ranks for a 1D array."""
        return np.argsort(np.argsort(column))

    def kendall_corr(data: np.ndarray) -> np.ndarray:
        """Calculate Kendall correlation matrix using NumPy."""
        logger.info("🔍 Computing Kendall correlation.")
        n_features = data.shape[1]
        corr_matrix = np.zeros((n_features, n_features))

        for i in range(n_features):
            for j in range(i, n_features):
                x, y = data[:, i], data[:, j]
                concordant = sum(
                    (x[k] - x[l]) * (y[k] - y[l]) > 0
                    for k in range(len(x))
                    for l in range(k + 1, len(x))
                )
                discordant = sum(
                    (x[k] - x[l]) * (y[k] - y[l]) < 0
                    for k in range(len(x))
                    for l in range(k + 1, len(x))
                )
                corr_matrix[i, j] = corr_matrix[j, i] = (concordant - discordant) / (
                    0.5 * len(x) * (len(x) - 1)
                )

        return corr_matrix
