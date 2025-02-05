import polars as pl
import plotly.express as px
from dash import Dash, Input, Output
from utils.store import Store

import plotly.graph_objects as go
import numpy as np


def register_missing_values_heatmap_callbacks(app: "Dash") -> None:
    """Registers callbacks for missing values heatmap visualization."""

    @app.callback(
        Output("missing-value-hist", "figure"),  # Populate missing values histogram
        Input("file-upload-status", "data"),  # Triggered when a file is uploaded
    )
    def update_missing_values_heatmap(file_uploaded):
        """Generates a missing value heatmap (similar to sns.heatmap(df.isnull()))."""
        print("Missing values heatmap callback triggered")

        if file_uploaded:
            df: pl.DataFrame = Store.get_static("data_frame")
            if df is not None:
                # Convert missing values to binary matrix (1 = missing, 0 = present)
                missing_matrix = df.select(
                    [df[col].is_null().cast(pl.Int8) for col in df.columns]
                ).to_numpy()

                if missing_matrix.sum() == 0:  # No missing values
                    return go.Figure()

                # Generate heatmap using plotly (similar to seaborn's sns.heatmap)
                fig = px.imshow(
                    missing_matrix,
                    labels={"x": "Features", "y": "Samples"},
                    x=df.columns,
                    color_continuous_scale="cividis",  # Matches Seaborn's default
                    # title="Heatmap of Missing Values",
                )

                fig.update_layout(
                    coloraxis_colorbar=dict(
                        title="Missing Values",
                        tickvals=[0, 1],
                        ticktext=["Present", "Missing"],
                    ),
                    xaxis=dict(tickangle=-45),
                )

                return fig

        return go.Figure()  # Return empty figure if no missing values
