import logging
import polars as pl
import dash_bootstrap_components as dbc
from dash import html, dash_table, Input, Output
from components.table import table_component
from utils.store import Store
from scipy.stats import skew, kurtosis, gaussian_kde
import numpy as np
from dash import Dash
import plotly.graph_objects as go
import plotly.express as px
from utils.logger_config import logger  # Import logger


def register_statistic_table_callbacks(app: "Dash") -> None:
    """Registers callbacks for computing and displaying statistical metrics."""

    @app.callback(
        Output("stats-table", "children"),  # Populate the stats table
        Input("file-upload-status", "data"),  # Triggered when a file is uploaded
    )
    def update_stats_table(file_uploaded):
        """Compute and display the statistical summary of the dataset."""
        if not file_uploaded:
            logger.warning("⚠️ No dataset uploaded. Skipping statistical summary.")
            return "No data available for statistical summary."

        df: pl.DataFrame = Store.get_static("data_frame")

        if df is None:
            logger.error("❌ Dataset not found in memory despite file upload.")
            return "No data available for statistical summary."

        try:
            # Compute statistical summary using Polars
            stats = df.describe()
            logger.info("✅ Successfully computed dataset statistics.")
            return table_component(stats)
        except Exception as e:
            logger.error(f"❌ Error while computing dataset statistics: {e}")
            return "❌ Failed to compute statistics."

    @app.callback(
        [
            Output("skewness-kurtosis-table", "children"),  # Skewness & Kurtosis Table
            Output("kde-plot", "figure"),  # Histogram + KDE Plot
        ],
        Input("file-upload-status", "data"),  # Triggered when a file is uploaded
        Input("column-dropdown", "value"),  # Selected feature
    )
    def update_skewness_kurtosis_table(file_uploaded, selected_column):
        """Compute and display skewness, kurtosis, and KDE plot for numerical features."""
        if not file_uploaded:
            logger.warning(
                "⚠️ No dataset uploaded. Skipping skewness & kurtosis calculation."
            )
            return "No valid data for analysis.", go.Figure()

        df: pl.DataFrame = Store.get_static("data_frame")

        if df is None:
            logger.error("❌ Dataset not found in memory despite file upload.")
            return "No valid data for analysis.", go.Figure()

        if not selected_column:
            logger.warning("⚠️ No column selected for skewness & kurtosis analysis.")
            return "No valid data for analysis.", go.Figure()

        if selected_column not in df.columns:
            logger.error(f"❌ Column '{selected_column}' not found in dataset.")
            return "No valid data for analysis.", go.Figure()

        logger.info(
            f"🔍 Computing skewness, kurtosis, and KDE for '{selected_column}'."
        )

        try:
            # Drop missing values
            column_data = np.array(df[selected_column].drop_nulls().to_list())

            if column_data.size == 0:
                logger.warning(
                    f"⚠️ No valid numeric data available for '{selected_column}' after removing NaNs."
                )
                return "No valid data for analysis.", go.Figure()

            # Compute skewness & kurtosis
            skew_value = skew(column_data, nan_policy="omit")
            kurtosis_value = kurtosis(column_data, nan_policy="omit")

            # **Prepare Skewness & Kurtosis Table**
            skew_kurt_df = pl.DataFrame(
                {
                    "Feature": [selected_column],
                    "Skewness": [skew_value],
                    "Kurtosis": [kurtosis_value],
                }
            )

            table = dash_table.DataTable(
                data=skew_kurt_df.to_dicts(),
                columns=[
                    {"name": "Feature", "id": "Feature"},
                    {"name": "Skewness", "id": "Skewness"},
                    {"name": "Kurtosis", "id": "Kurtosis"},
                ],
                style_table={"maxHeight": "400px", "overflowY": "auto"},
                page_size=10,
                style_cell={"textAlign": "left", "whiteSpace": "normal"},
                style_header={"backgroundColor": "lightgrey", "fontWeight": "bold"},
            )

            # **Compute KDE Curve**
            kde = gaussian_kde(column_data)
            x_vals = np.linspace(column_data.min(), column_data.max(), 100)
            y_vals = kde(x_vals)

            # **Create Histogram**
            fig = go.Figure()
            fig.add_trace(
                go.Histogram(
                    x=column_data,
                    nbinsx=30,
                    name="Histogram",
                    opacity=0.7,
                    marker=dict(color="blue"),
                )
            )

            # **Overlay KDE Line**
            fig.add_trace(
                go.Scatter(
                    x=x_vals,
                    y=y_vals
                    * column_data.size
                    * (x_vals.max() - x_vals.min())
                    / 30,  # Scale to histogram
                    mode="lines",
                    name="KDE Density",
                    line=dict(color="red", width=2),
                )
            )

            # **Set Layout**
            fig.update_layout(
                title=f"Histogram & KDE for {selected_column}",
                xaxis_title=selected_column,
                yaxis_title="Density / Frequency",
                template="plotly_white",
                showlegend=True,
            )

            logger.info(f"✅ Successfully generated KDE plot for '{selected_column}'.")
            return table, fig

        except Exception as e:
            logger.error(f"❌ Error while computing skewness, kurtosis, or KDE: {e}")
            return "❌ Failed to compute analysis.", go.Figure()
