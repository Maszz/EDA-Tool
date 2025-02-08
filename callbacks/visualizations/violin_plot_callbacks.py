import logging
import polars as pl
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from dash import Input, Output
from utils.store import Store
from utils.logger_config import logger  # Import logger


def register_violin_plot_callbacks(app):
    """Registers callbacks for the Violin Plot visualization."""

    @app.callback(
        Output("violin-plot", "figure"),
        Input("file-upload-status", "data"),
        Input("categorical-dropdown", "value"),
        Input("numeric-dropdown", "value"),
    )
    def update_violin_plot(file_uploaded, categorical_feature, numerical_feature):
        """Generates a violin plot for a numerical feature grouped by a categorical feature with error handling."""

        if not file_uploaded:
            logger.warning("⚠️ No dataset uploaded. Clearing Violin plot.")
            return go.Figure()

        df: pl.DataFrame = Store.get_static("data_frame")

        if df is None:
            logger.error("❌ Dataset not found in memory despite file upload.")
            return go.Figure()

        if not categorical_feature or not numerical_feature:
            logger.warning("⚠️ Missing feature selection for Violin plot.")
            return go.Figure()

        if categorical_feature not in df.columns or numerical_feature not in df.columns:
            logger.error(
                f"❌ Selected features {categorical_feature} or {numerical_feature} not found in dataset."
            )
            return go.Figure()

        try:
            # Extract selected features and drop missing values
            clean_df = df.select([categorical_feature, numerical_feature]).drop_nulls()

            # Ensure sufficient data points
            if clean_df.height < 2:
                logger.warning("⚠️ Insufficient valid data points for Violin plot.")
                return go.Figure()

            # Convert Polars DataFrame to dictionary format for Plotly
            fig = px.violin(
                clean_df.to_dicts(),
                x=categorical_feature,
                y=numerical_feature,
                box=True,
                points="all",
                title=f"Violin Plot: {numerical_feature} by {categorical_feature}",
                labels={
                    categorical_feature: "Category",
                    numerical_feature: "Value",
                },
                template="plotly_white",
            )

            logger.info(
                f"✅ Successfully generated Violin plot for {numerical_feature} grouped by {categorical_feature}."
            )
            return fig

        except Exception as e:
            logger.error(f"❌ Error generating Violin plot: {e}")
            return go.Figure()
