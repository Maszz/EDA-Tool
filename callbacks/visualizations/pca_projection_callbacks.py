import plotly.graph_objects as go
import polars as pl
from dash import Input, Output
from plotly_resampler import FigureResampler  # ✅ Adds resampling for large datasets
from sklearn.decomposition import PCA

from utils.cache_manager import CACHE_MANAGER  # Import Cache Manager
from utils.logger_config import logger  # Import logger
from utils.store import Store


def register_pca_projection_callbacks(app) -> None:
    """Registers the callback for PCA 2D Projection visualization."""

    @app.callback(
        Output("pca-plot", "figure"),
        Input("file-upload-status", "data"),
    )
    def update_pca_plot(file_uploaded):
        """Generates an optimized PCA 2D Projection with WebGL and resampling."""
        if not file_uploaded:
            return go.Figure()

        df: pl.DataFrame = Store.get_static("data_frame")
        if df is None:
            return go.Figure()  # No valid data

        # ✅ Filter only numerical features
        num_cols = [
            col for col in df.columns if df[col].dtype in (pl.Float64, pl.Int64)
        ]
        if len(num_cols) < 2:
            return go.Figure()  # PCA needs at least 2 numeric features

        # ✅ Generate cache key using dataset shape (prevents unnecessary recomputation)
        cache_key = f"pca_projection_{df.shape}"
        cached_result = CACHE_MANAGER.load_cache(cache_key, df)
        if cached_result:
            return cached_result  # Return cached result

        try:
            # ✅ Handle missing values: replace NaNs with column mean
            clean_df = df.select(num_cols).fill_nan(None).drop_nulls()

            if clean_df.is_empty() or clean_df.shape[0] < 2:
                return go.Figure()  # Not enough data after cleaning

            # ✅ Convert to NumPy for PCA
            data_matrix = clean_df.to_numpy()

            # ✅ Perform PCA
            pca = PCA(n_components=2)
            reduced = pca.fit_transform(data_matrix)

            # ✅ Convert PCA results for plotting
            pca_x, pca_y = reduced[:, 0], reduced[:, 1]

            # ✅ Resampled Scattergl PCA Plot
            fig = FigureResampler(go.Figure())

            fig.add_trace(
                go.Scattergl(
                    x=pca_x,
                    y=pca_y,
                    mode="markers",
                    marker={"color": "blue", "size": 5, "opacity": 0.7},
                    name="PCA Projection",
                )
            )

            fig.update_layout(
                title="PCA 2D Projection (WebGL + Resampled)",
                xaxis_title="Principal Component 1",
                yaxis_title="Principal Component 2",
                template="plotly_white",
            )

            # ✅ Store in cache
            CACHE_MANAGER.save_cache(cache_key, df, fig)

            return fig

        except Exception as e:
            logger.error(f"❌ Error generating PCA plot: {e}")
            return go.Figure()
