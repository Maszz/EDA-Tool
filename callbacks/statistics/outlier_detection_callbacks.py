import numpy as np
import plotly.express as px
import plotly.graph_objects as go
import polars as pl
from dash import Dash, Input, Output
from plotly_resampler import FigureResampler
from sklearn.cluster import DBSCAN
from sklearn.ensemble import IsolationForest

from utils.cache_manager import CACHE_MANAGER  # Import cache manager
from utils.logger_config import logger  # Import logger
from utils.store import Store


def register_outlier_detection_callbacks(app: "Dash") -> None:
    """Registers callbacks for outlier detection using multiple algorithms."""





def register_outlier_detection_callbacks(app: "Dash") -> None:
    """Registers callbacks for detecting outliers using different algorithms."""

    @app.callback(
        Output("outlier-boxplot", "figure"),  # ✅ Boxplot uses FigureResampler
        Output("outlier-scatter", "figure"),  # ✅ Scatter uses OpenGL (Scattergl)
        Input("column-dropdown", "value"),
        Input("outlier-algo-dropdown", "value"),
        Input("file-upload-status", "data"),  # ✅ Now triggers on file upload
    )
    def update_outlier_boxplot(column_name, algorithm, file_uploaded):
        """
        Creates two figures:
        1️⃣ A resampled boxplot (optimized for large datasets)
        2️⃣ A separate scatter plot using OpenGL (`Scattergl`) to display outliers.
        """
        if not file_uploaded:
            return go.Figure(), go.Figure()  # No unnecessary logging

        df: pl.DataFrame = Store.get_static("data_frame")
        if df is None or column_name not in df.columns:
            return go.Figure(), go.Figure()  # Handle missing data gracefully

        # Generate cache key
        cache_key = f"outlier_detection_{column_name}_{algorithm}"
        cached_result = CACHE_MANAGER.load_cache(cache_key, df)
        if cached_result:
            return cached_result  # Return cached results if available

        try:
            logger.info(f"🔍 Detecting outliers in '{column_name}' using {algorithm}.")

            # Convert column to NumPy and drop NaNs
            column_data = df[column_name].to_numpy()
            column_data_clean = column_data[~np.isnan(column_data)]  # Remove NaNs

            if column_data_clean.size == 0:
                return (
                    go.Figure(),
                    go.Figure(),
                )  # No valid data, avoid logging redundant warnings

            # Detect outliers
            outliers = detect_outliers(column_data_clean, algorithm)
            if outliers is None:
                return go.Figure(), go.Figure()  # Return empty if unsupported algorithm

            ### **1️⃣ First Figure: Boxplot (Resampled for Performance)**
            fig_box = FigureResampler(
                px.box(
                    y=column_data_clean,
                    points="all",
                    title=f"Outlier Detection (Optimized) - {column_name} ({algorithm.capitalize()})",
                    labels={"y": column_name},
                    template="plotly_white",
                )
            )

            ### **2️⃣ Second Figure: Scatter Plot (OpenGL)**
            fig_scatter = go.Figure()

            # **Plot all data points using OpenGL (`Scattergl`)**
            fig_scatter.add_trace(
                go.Scattergl(
                    x=["Outliers"] * np.sum(outliers),
                    y=column_data_clean,
                    mode="markers",
                    marker={"color": "blue", "size": 6, "opacity": 0},
                    name="All Data Points",
                )
            )

            # **Highlight Outliers using OpenGL (`Scattergl`)**
            fig_scatter.add_trace(
                go.Scattergl(
                    x=["Outliers"] * np.sum(outliers),
                    y=column_data_clean[outliers],
                    mode="markers",
                    marker={"color": "red", "size": 8, "opacity": 1},
                    name="Outliers",
                )
            )

            fig_scatter.update_layout(
                template="plotly_white",
                yaxis_title=column_name,
                title=f"Outlier - {column_name} ({algorithm.capitalize()})",
                showlegend=False,  # ✅ Hide legend for minimal display
                xaxis={"visible": False},  # ✅ Hide x-axis
                yaxis={
                    "visible": False,  # ✅ Hide y-axis
                    # showgrid=False,  # ✅ Remove grid lines
                    # zeroline=False,  # ✅ Remove zero line
                    # title="",  # ✅ No y-axis title for minimalism
                    # matches="y",  # ✅ Ensures y-scale matches first figure (boxplot)
                },
                # margin=dict(r=200),  # ✅ Minimal margin to keep it compact
                # width=250,  # ✅ Adjusts figure width to be more narrow
                # height=300,  # ✅ Keeps height aligned with the boxplot
            )

            # Store in cache
            CACHE_MANAGER.save_cache(cache_key, df, (fig_box, fig_scatter))
            return fig_box, fig_scatter

        except Exception as e:
            logger.error(f"❌ Error during outlier detection: {e}")
            return go.Figure(), go.Figure()  # Return empty figures


def detect_outliers(data: np.ndarray, algorithm: str):
    """Detects outliers using the selected algorithm."""
    if algorithm == "zscore":
        return detect_outliers_zscore(data)
    elif algorithm == "iqr":
        return detect_outliers_iqr(data)
    elif algorithm == "dbscan":
        return detect_outliers_dbscan(data)
    elif algorithm == "isolation_forest":
        return detect_outliers_isolation_forest(data)
    else:
        logger.error(f"❌ Unsupported algorithm: {algorithm}")
        return None


# ✅ **Outlier Detection Methods (No Change)**
def detect_outliers_zscore(data: np.ndarray, threshold: float = 3.0) -> np.ndarray:
    """Detect outliers using Z-Score method (Handles NaNs)."""
    if data.size == 0:
        return np.array([])  # Return empty if no data
    z_scores = np.abs((data - np.mean(data)) / np.std(data))
    return z_scores > threshold


def detect_outliers_iqr(data: np.ndarray) -> np.ndarray:
    """Detect outliers using Interquartile Range (IQR) (Handles NaNs)."""
    if data.size == 0:
        return np.array([])  # Return empty if no data
    q1, q3 = np.percentile(data, [25, 75])
    iqr = q3 - q1
    lower_bound = q1 - 1.5 * iqr
    upper_bound = q3 + 1.5 * iqr
    return (data < lower_bound) | (data > upper_bound)


def detect_outliers_dbscan(
    data: np.ndarray, eps: float = 0.5, min_samples: int = 5
) -> np.ndarray:
    """Detect outliers using DBSCAN clustering (Handles NaNs)."""
    if data.size == 0:
        return np.array([])  # Return empty if no data
    dbscan = DBSCAN(eps=eps, min_samples=min_samples)
    labels = dbscan.fit_predict(data.reshape(-1, 1))
    return labels == -1  # Outliers are labeled as -1


def detect_outliers_isolation_forest(data: np.ndarray) -> np.ndarray:
    """Detect outliers using Isolation Forest (Handles NaNs)."""
    if data.size == 0:
        return np.array([])  # Return empty if no data
    model = IsolationForest(contamination=0.05, random_state=42)
    model.fit(data.reshape(-1, 1))
    outliers = model.predict(data.reshape(-1, 1))
    return outliers == -1  # Outliers are labeled as -1
