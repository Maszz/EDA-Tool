import logging
import polars as pl
import plotly.express as px
import plotly.graph_objects as go
from dash import Dash, Input, Output
from utils.store import Store
from utils.logger_config import logger  # Import logger
from utils.cache_manager import CACHE_MANAGER  # Import cache manager


def register_missing_values_callbacks(app: "Dash") -> None:
    """Registers callbacks for missing values heatmap visualization."""

    @app.callback(
        Output("missing-value-heat", "figure"),  # Populate missing values heatmap
        Input("file-upload-status", "data"),  # Triggered when a file is uploaded
    )
    def update_missing_values_heatmap(file_uploaded):
        """Generates a missing value heatmap (similar to sns.heatmap(df.isnull())) with caching."""

        if not file_uploaded:
            logger.warning("⚠️ No dataset loaded. Skipping missing values heatmap.")
            return go.Figure()

        df: pl.DataFrame = Store.get_static("data_frame")

        if df is None:
            logger.error("❌ Dataset not found in memory despite file upload.")
            return go.Figure()

        # ✅ Check cache before recalculating
        cache_key = "missing_values_heatmap"
        cached_result = CACHE_MANAGER.load_cache(cache_key, df)
        if cached_result:
            logger.info("🔄 Loaded cached missing values heatmap.")
            return cached_result  # Return cached result instantly

        # Convert missing values to binary matrix (1 = missing, 0 = present)
        missing_matrix = df.select(
            [df[col].is_null().cast(pl.Int8) for col in df.columns]
        ).to_numpy()

        total_missing = missing_matrix.sum()

        if total_missing == 0:
            logger.info("✅ No missing values found in the dataset.")
            return go.Figure()

        logger.info(f"🔍 Missing values detected: {total_missing} missing entries.")

        # Generate heatmap using Plotly (similar to Seaborn's sns.heatmap)
        fig = px.imshow(
            missing_matrix,
            labels={"x": "Features", "y": "Samples"},
            x=df.columns,
            color_continuous_scale="cividis",  # Matches Seaborn's default
        )

        fig.update_layout(
            coloraxis_colorbar={
                "title": "Missing Values",
                "tickvals": [0, 1],
                "ticktext": ["Present", "Missing"],
            },
            xaxis={"tickangle": -45},
        )

        # ✅ Store result in cache
        CACHE_MANAGER.save_cache(cache_key, df, fig)
        logger.info("💾 Cached missing values heatmap for future use.")

        return fig
