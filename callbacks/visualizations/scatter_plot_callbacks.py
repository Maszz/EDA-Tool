import plotly.graph_objects as go
import polars as pl
from dash import Input, Output
from plotly_resampler import FigureResampler  # ✅ Adds resampling for large datasets

from utils.cache_manager import CACHE_MANAGER  # Import Cache Manager
from utils.logger_config import logger  # Import logger
from utils.store import Store


def register_scatter_plot_callbacks(app) -> None:
    """Registers callbacks for the Scatter Plot visualization."""

    @app.callback(
        Output("scatter-plot", "figure"),
        Input("file-upload-status", "data"),
        Input("feature-x-dropdown", "value"),
        Input("feature-y-dropdown", "value"),
    )
    def update_scatter_plot(file_uploaded, feature_x, feature_y):
        """Generates an optimized Scatter plot with WebGL and resampling, supporting same X and Y columns."""
        if not file_uploaded:
            return go.Figure()

        df: pl.DataFrame = Store.get_static("data_frame")
        if df is None or not feature_x or not feature_y:
            return go.Figure()  # No valid data

        # ✅ Check if selected features exist
        if feature_x not in df.columns or feature_y not in df.columns:
            return go.Figure()  # Invalid feature selection

        # ✅ Handle duplicate column names by renaming the Y-axis column if needed
        if feature_x == feature_y:
            feature_y_renamed = f"{feature_y}_y"
            df = df.with_columns(df[feature_y].alias(feature_y_renamed))
            feature_y = feature_y_renamed  # Use new alias for processing

        # ✅ Generate cache key using dataset shape (prevents unnecessary recomputation)
        cache_key = f"scatter_{feature_x}_{feature_y}_{df.shape}"
        cached_result = CACHE_MANAGER.load_cache(cache_key, df)
        if cached_result:
            return cached_result  # Return cached result

        try:
            # ✅ Extract feature data (handling NaNs)
            df_clean = df.select([feature_x, feature_y]).drop_nulls()
            if df_clean.is_empty():
                return go.Figure()  # No valid data

            x_data, y_data = (
                df_clean[feature_x].to_numpy(),
                df_clean[feature_y].to_numpy(),
            )

            # ✅ Resampled Scattergl Plot
            fig = FigureResampler(go.Figure())

            fig.add_trace(
                go.Scattergl(
                    x=x_data,
                    y=y_data,
                    mode="markers",
                    marker={"color": "blue", "size": 5, "opacity": 0.7},
                    name=f"{feature_x} vs {feature_y.replace('_y', '')}",
                )
            )

            fig.update_layout(
                title=f"Scatter Plot: {feature_x} vs {feature_y.replace('_y', '')} (WebGL + Resampled)",
                xaxis_title=feature_x,
                yaxis_title=feature_y.replace("_y", ""),  # Remove alias in display
                template="plotly_white",
            )

            # ✅ Store in cache
            CACHE_MANAGER.save_cache(cache_key, df, fig)

            return fig

        except Exception as e:
            logger.error(f"❌ Error generating Scatter plot: {e}")
            return go.Figure()
