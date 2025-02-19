import numpy as np
import plotly.graph_objects as go
import polars as pl
from dash import Input, Output
from plotly_resampler import FigureResampler
from scipy.stats import gaussian_kde  # Import Gaussian KDE for contour

from utils.cache_manager import CACHE_MANAGER
from utils.logger_config import logger
from utils.store import Store


def register_scatter_plot_callbacks(app) -> None:
    """Registers callbacks for Scatter and Contour Plot visualization."""

    @app.callback(
        Output("scatter-plot", "figure"),
        Input("file-upload-status", "data"),
        Input("feature-x-dropdown", "value"),
        Input("feature-y-dropdown", "value"),
        Input("scatter-contour-toggle", "value"),  # Toggle between Scatter and Contour
    )
    def update_scatter_or_contour_plot(file_uploaded, feature_x, feature_y, plot_type):
        """Generates either a Scatter Plot or a Contour Plot based on user selection."""
        if not file_uploaded:
            return go.Figure()

        df: pl.DataFrame = Store.get_static("data_frame")
        if df is None or not feature_x or not feature_y:
            return go.Figure()  # No valid data

        # ✅ Check if selected features exist
        if feature_x not in df.columns or feature_y not in df.columns:
            return go.Figure()  # Invalid feature selection

        # ✅ Handle duplicate column names
        if feature_x == feature_y:
            feature_y_renamed = f"{feature_y}_y"
            df = df.with_columns(df[feature_y].alias(feature_y_renamed))
            feature_y = feature_y_renamed

        # ✅ Generate cache key using dataset shape and selected mode
        cache_key = f"{plot_type}_{feature_x}_{feature_y}"
        cached_result = CACHE_MANAGER.load_cache(cache_key, df)
        if cached_result:
            return cached_result

        try:
            # ✅ Extract feature data (handling NaNs)
            df_clean = df.select([feature_x, feature_y]).drop_nulls()
            if df_clean.is_empty():
                return go.Figure()  # No valid data

            # ✅ Sort data by x-axis
            df_clean = df_clean.sort(feature_x)

            x_data, y_data = (
                df_clean[feature_x].to_numpy(),
                df_clean[feature_y].to_numpy(),
            )

            fig = go.Figure()

            if plot_type == "scatter":
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
                    title=f"Scatter Plot: {feature_x} vs {feature_y.replace('_y', '')}",
                    xaxis_title=feature_x,
                    yaxis_title=feature_y.replace("_y", ""),
                    template="plotly_white",
                )

            elif plot_type == "contour":
                # ✅ Estimate density using KDE
                kde = gaussian_kde(np.vstack([x_data, y_data]))
                x_grid, y_grid = np.meshgrid(
                    np.linspace(x_data.min(), x_data.max(), 100),
                    np.linspace(y_data.min(), y_data.max(), 100),
                )
                density = kde(np.vstack([x_grid.ravel(), y_grid.ravel()])).reshape(
                    100, 100
                )

                # ✅ Create contour plot
                fig.add_trace(
                    go.Contour(
                        x=np.linspace(x_data.min(), x_data.max(), 100),
                        y=np.linspace(y_data.min(), y_data.max(), 100),
                        z=density,
                        colorscale="Viridis",
                        contours=dict(showlabels=True, size=2),
                    )
                )

                fig.update_layout(
                    title=f"Contour Plot: {feature_x} vs {feature_y.replace('_y', '')}",
                    xaxis_title=feature_x,
                    yaxis_title=feature_y.replace("_y", ""),
                    template="plotly_white",
                )

            # ✅ Store in cache
            CACHE_MANAGER.save_cache(cache_key, df, fig)

            return fig

        except Exception as e:
            logger.error(f"❌ Error generating {plot_type} plot: {e}")
            return go.Figure()
