import logging
import polars as pl
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from dash import Input, Output
from utils.store import Store
from utils.logger_config import logger  # Import logger


def register_pair_plot_callbacks(app):
    """Registers callbacks for the Pair Plot visualization."""

    @app.callback(
        Output("pair-plot", "figure"),
        Input("file-upload-status", "data"),
        Input("pairplot-features-dropdown", "value"),
    )
    def update_pair_plot(file_uploaded, selected_features):
        """Generates a pair plot for selected numerical features."""

        if not file_uploaded:
            logger.warning("⚠️ No dataset uploaded. Clearing pair plot.")
            return go.Figure()

        df: pl.DataFrame = Store.get_static("data_frame")

        if df is None:
            logger.error("❌ Dataset not found in memory despite file upload.")
            return go.Figure()

        if not selected_features or not all(
            col in df.columns for col in selected_features
        ):
            logger.warning(
                f"⚠️ Invalid or missing features selected: {selected_features}"
            )
            return go.Figure()

        try:
            # Convert selected features to NumPy array
            data = np.column_stack([df[col].to_numpy() for col in selected_features])

            # Convert back to Polars DataFrame with correct column names
            pairplot_df = pl.DataFrame(data, schema=selected_features)

            # Generate scatter matrix (Pair Plot)
            fig = px.scatter_matrix(
                pairplot_df,
                dimensions=selected_features,
                title="Pair Plot of Selected Features",
                template="plotly_white",
            )

            logger.info(
                f"✅ Successfully generated pair plot for features: {selected_features}"
            )
            return fig

        except Exception as e:
            logger.error(f"❌ Error generating pair plot: {e}")
            return go.Figure()
