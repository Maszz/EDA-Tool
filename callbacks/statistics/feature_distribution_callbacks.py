import logging
import numpy as np
import plotly.graph_objects as go
import polars as pl
from dash import Dash, Input, Output
from plotly_resampler import FigureResampler
from utils.store import Store
from utils.logger_config import logger
from utils.cache_manager import CACHE_MANAGER
from scipy.stats import skew, kurtosis, gaussian_kde
from dash import dash_table


def register_feature_distribution_callbacks(app: "Dash") -> None:
    """Registers callbacks for generating downsampled histograms."""

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
            return "No valid data for analysis.", go.Figure()

        df: pl.DataFrame = Store.get_static("data_frame")

        if df is None or not selected_column or selected_column not in df.columns:
            return "No valid data for analysis.", go.Figure()

        # Generate cache key
        cache_key = f"skewness_kurtosis_{selected_column}"
        cached_result = CACHE_MANAGER.load_cache(cache_key, df)
        if cached_result:
            return cached_result

        try:
            logger.info(
                f"🔍 Computing skewness, kurtosis, and KDE for '{selected_column}'."
            )

            # Drop missing values efficiently
            column_data = np.asarray(
                df[selected_column].drop_nulls().to_list(), dtype=np.float64
            )

            if column_data.size == 0:
                return "No valid data for analysis.", go.Figure()

            # Compute skewness & kurtosis (handling NaNs better)
            skew_value = np.nan_to_num(skew(column_data, nan_policy="omit"), nan=0.0)
            kurtosis_value = np.nan_to_num(
                kurtosis(column_data, nan_policy="omit"), nan=0.0
            )

            # **Prepare Skewness & Kurtosis Table**
            table = dash_table.DataTable(
                data=[
                    {
                        "Feature": selected_column,
                        "Skewness": round(skew_value, 4),
                        "Kurtosis": round(kurtosis_value, 4),
                    }
                ],
                columns=[
                    {"name": "Feature", "id": "Feature"},
                    {"name": "Skewness", "id": "Skewness"},
                    {"name": "Kurtosis", "id": "Kurtosis"},
                ],
                style_table={"maxHeight": "400px", "overflowY": "auto"},
                page_size=1,
                style_cell={"textAlign": "center", "whiteSpace": "normal"},
                style_header={"backgroundColor": "#f8f9fa", "fontWeight": "bold"},
            )

            # **Compute KDE Curve**
            kde = gaussian_kde(column_data)
            x_vals = np.linspace(column_data.min(), column_data.max(), 100)
            y_vals = kde(x_vals)

            # **Create Downsampled Histogram**
            fig = FigureResampler(go.Figure())
            fig.add_trace(
                go.Histogram(
                    x=column_data,
                    nbinsx=30,
                    name="Histogram",
                    opacity=0.7,
                    marker=dict(color="blue"),
                )
            )

            # **Overlay KDE Line (Adjusted Scaling)**
            fig.add_trace(
                go.Scatter(
                    x=x_vals,
                    y=y_vals
                    * np.ptp(column_data)
                    * column_data.size
                    / 30,  # ✅ Smarter scaling
                    mode="lines",
                    name="KDE Density",
                    line=dict(color="red", width=2),
                )
            )

            # **Set Layout**
            fig.update_layout(
                title=f"Feature Distribution (Histogram & KDE) - {selected_column}",
                xaxis_title=selected_column,
                yaxis_title="Density / Frequency",
                template="plotly_white",
                showlegend=True,
            )

            logger.info(f"✅ Successfully generated KDE plot for '{selected_column}'.")

            # Store in cache
            result = (table, fig)
            CACHE_MANAGER.save_cache(cache_key, df, result)

            return result

        except Exception as e:
            logger.error(f"❌ Error while computing skewness, kurtosis, or KDE: {e}")
            return "❌ Failed to compute analysis.", go.Figure()
