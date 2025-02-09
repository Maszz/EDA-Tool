import plotly.express as px
import plotly.graph_objects as go
import polars as pl
from dash import Input, Output

from utils.cache_manager import CACHE_MANAGER  # Import Cache Manager
from utils.logger_config import logger  # Import logger
from utils.store import Store


def register_bar_plot_callbacks(app) -> None:
    """Registers callbacks for the Bar Plot visualization."""

    @app.callback(
        Output("bar-plot", "figure"),
        Input("file-upload-status", "data"),
        Input("categorical-dropdown", "value"),
    )
    def update_bar_plot(file_uploaded, selected_categorical):
        """Generates an optimized bar plot for categorical feature distribution."""
        if not file_uploaded:
            return go.Figure()

        df: pl.DataFrame = Store.get_static("data_frame")
        if df is None or selected_categorical not in df.columns:
            return go.Figure()  # No valid data

        # ✅ Generate cache key using dataset shape (prevents unnecessary recomputation)
        cache_key = f"bar_plot_{selected_categorical}_{df.shape}"
        cached_result = CACHE_MANAGER.load_cache(cache_key, df)
        if cached_result:
            return cached_result  # Return cached result

        try:
            # ✅ Get value counts
            category_counts = df[selected_categorical].value_counts()

            # ✅ Inspect actual column names (Polars may return different names)
            col_names = category_counts.columns
            logger.info(f"🔍 Found columns in value_counts(): {col_names}")

            # ✅ Rename columns dynamically based on available names
            category_col = col_names[0]  # The categorical feature name
            count_col = col_names[1]  # The count column

            category_counts = category_counts.rename(
                {category_col: "category", count_col: "count"}
            )

            unique_values = category_counts["category"].to_list()
            counts = category_counts["count"].to_list()

            if not unique_values:
                return go.Figure()

            # ✅ Create Bar Plot
            fig = px.bar(
                x=unique_values,
                y=counts,
                title=f"Bar Plot: {selected_categorical}",
                labels={"x": selected_categorical, "y": "Count"},
                template="plotly_white",
            )

            # ✅ Store in cache
            CACHE_MANAGER.save_cache(cache_key, df, fig)

            return fig

        except Exception as e:
            logger.error(
                f"❌ Error generating bar plot for '{selected_categorical}': {e}"
            )
            return go.Figure()
