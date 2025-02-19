import plotly.graph_objects as go
import polars as pl
from dash import Input, Output
from plotly_resampler import FigureResampler  # ✅ Adds resampling for large datasets

from utils.cache_manager import CACHE_MANAGER  # Import Cache Manager
from utils.logger_config import logger  # Import logger
from utils.store import Store


def register_violin_plot_callbacks(app) -> None:
    """Registers callbacks for the Violin Plot visualization with caching and resampling."""

    @app.callback(
        Output("violin-plot", "figure"),
        Input("file-upload-status", "data"),
        Input("categorical-dropdown", "value"),
        Input("numeric-dropdown", "value"),
    )
    def update_violin_plot(file_uploaded, categorical_feature, numerical_feature):
        """Generates an optimized violin plot for a numerical feature grouped by a categorical feature."""
        if not file_uploaded:
            return _log_and_return_empty("⚠️ No dataset uploaded. Clearing Violin plot.")

        df: pl.DataFrame = Store.get_static("data_frame")
        if df is None:
            return _log_and_return_empty("❌ Dataset not found in memory.")

        if not categorical_feature or not numerical_feature:
            return _log_and_return_empty("⚠️ Missing feature selection for Violin plot.")

        if categorical_feature not in df.columns or numerical_feature not in df.columns:
            return _log_and_return_empty(
                f"❌ Selected features {categorical_feature} or {numerical_feature} not found in dataset."
            )

        # ✅ Handle duplicate column names by renaming the numerical column
        if categorical_feature == numerical_feature:
            numerical_feature_alias = f"{numerical_feature}_value"
            df = df.with_columns(df[numerical_feature].alias(numerical_feature_alias))
            numerical_feature = numerical_feature_alias  # Use new alias for processing

        # ✅ Generate cache key using dataset shape (prevents unnecessary recomputation)
        cache_key = f"violin_{categorical_feature}_{numerical_feature}"
        cached_result = CACHE_MANAGER.load_cache(cache_key, df)
        if cached_result:
            x_data, y_data = cached_result
        else:
            try:
                # ✅ Extract selected features and drop missing values
                clean_df = df.select(
                    [categorical_feature, numerical_feature]
                ).drop_nulls()

                # ✅ Ensure sufficient data points
                if clean_df.height < 2:
                    return _log_and_return_empty(
                        "⚠️ Insufficient valid data points for Violin plot."
                    )

                x_data = clean_df[categorical_feature].to_numpy()
                y_data = clean_df[numerical_feature].to_numpy()

                # ✅ Store minimal data in cache
                CACHE_MANAGER.save_cache(
                    cache_key,
                    df,
                    (x_data, y_data),
                )

            except Exception as e:
                logger.error(f"❌ Error generating Violin plot: {e}")
                return go.Figure()

        # ✅ Create Resampler Figure
        fig = FigureResampler(go.Figure())

        # ✅ Add violin plot trace
        fig.add_trace(
            go.Violin(
                x=x_data,
                y=y_data,
                box_visible=True,
                meanline_visible=True,
                points="all",
                name=f"{numerical_feature} by {categorical_feature}",
            )
        )

        fig.update_layout(
            title=f"Violin Plot: {numerical_feature} by {categorical_feature} (Resampled)",
            xaxis_title=categorical_feature,
            yaxis_title=numerical_feature,
            template="plotly_white",
        )

        logger.info("✅ Successfully generated resampled Violin plot.")
        return fig


def _log_and_return_empty(message: str):
    """Helper function to log a warning and return an empty figure."""
    logger.warning(message)
    return go.Figure()
