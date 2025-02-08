import logging
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
import polars as pl
from dash import Dash, Input, Output, State
from sklearn.ensemble import IsolationForest
from sklearn.cluster import DBSCAN
from utils.store import Store
from utils.logger_config import logger  # Import logger


def register_outlier_detection_callbacks(app: "Dash") -> None:
    """Registers callbacks for outlier detection using multiple algorithms."""

    @app.callback(
        Output("outlier-boxplot", "figure"),  # Update outlier visualization
        Input("column-dropdown", "value"),  # Selected feature
        Input("outlier-algo-dropdown", "value"),  # Selected algorithm
        State("file-upload-status", "data"),  # Ensure file is uploaded
    )
    def update_outlier_boxplot(column_name, algorithm, file_uploaded):
        """Creates a boxplot for detecting outliers using the selected algorithm, with missing value handling."""
        if not file_uploaded:
            logger.warning("⚠️ No dataset uploaded. Skipping outlier detection.")
            return go.Figure()

        df: pl.DataFrame = Store.get_static("data_frame")

        if df is None:
            logger.error("❌ Dataset not found in memory despite file upload.")
            return go.Figure()

        if not column_name:
            logger.warning("⚠️ No column selected for outlier detection.")
            return go.Figure()

        if column_name not in df.columns:
            logger.error(f"❌ Column '{column_name}' not found in dataset.")
            return go.Figure()

        logger.info(f"🔍 Detecting outliers in '{column_name}' using {algorithm}.")

        try:
            # Convert column to NumPy and drop NaN values
            column_data = np.array(df[column_name].drop_nulls().to_list())

            if column_data.size == 0:
                logger.warning("⚠️ No valid numeric data available after removing NaNs.")
                return go.Figure()

            # Detect outliers based on selected algorithm
            if algorithm == "zscore":
                outliers = detect_outliers_zscore(column_data)
            elif algorithm == "iqr":
                outliers = detect_outliers_iqr(column_data)
            elif algorithm == "dbscan":
                outliers = detect_outliers_dbscan(column_data)
            elif algorithm == "isolation_forest":
                outliers = detect_outliers_isolation_forest(column_data)
            else:
                logger.error(f"❌ Unsupported algorithm: {algorithm}")
                return go.Figure()

            logger.info(
                f"✅ Outlier detection completed for '{column_name}' using {algorithm}."
            )

            # Create boxplot with outliers highlighted
            fig = px.box(
                y=column_data,
                points="all",  # Show all data points
                title=f"Outlier Detection in {column_name} ({algorithm.capitalize()})",
                labels={"y": column_name},
                template="plotly_white",
            )

            # Highlight detected outliers
            fig.add_scatter(
                x=["Outliers"] * np.sum(outliers),
                y=column_data[outliers],  # Outlier values
                mode="markers",
                marker={"color": "red", "size": 8},
                name="Outliers",
            )

            return fig

        except Exception as e:
            logger.error(f"❌ Error during outlier detection: {e}")
            return go.Figure()  # Return empty figure


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
