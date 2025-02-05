import polars as pl
import plotly.express as px
import plotly.graph_objects as go
from dash import Dash, Input, Output, State
from utils.store import Store
import numpy as np
from sklearn.ensemble import IsolationForest
from sklearn.cluster import DBSCAN


def register_outlier_detection_callbacks(app: "Dash") -> None:
    """Registers callbacks for outlier detection using multiple algorithms."""

    @app.callback(
        Output("outlier-boxplot", "figure"),  # Update outlier visualization
        Input("column-dropdown", "value"),  # Selected feature
        Input("outlier-algo-dropdown", "value"),  # Selected algorithm
        State("file-upload-status", "data"),  # Ensure file is uploaded
        prevent_initial_call=True,
    )
    def update_outlier_boxplot(column_name, algorithm, file_uploaded):
        """Creates a boxplot for detecting outliers using selected algorithm."""
        if file_uploaded and column_name and algorithm:
            print(f"Detecting outliers in {column_name} using {algorithm}")
            df: pl.DataFrame = Store.get_static("data_frame")
            if df is not None and column_name in df.columns:
                # Extract column data as a NumPy array
                column_data = np.array(df[column_name].to_list())

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
                    raise ValueError(f"Unsupported algorithm: {algorithm}")

                # Create boxplot with outliers highlighted
                fig = px.box(
                    y=column_data,
                    points="all",  # Show outliers
                    title=f"Outlier Detection in {column_name} ({algorithm.capitalize()})",
                    labels={"y": column_name},
                    template="plotly_white",
                )
                # Highlight detected outliers
                # Add scatter points for outliers aligned with the boxplot
                fig.add_scatter(
                    x=["Outliers"] * np.sum(outliers),
                    y=column_data[outliers],  # Outlier values
                    mode="markers",
                    marker={"color": "red", "size": 8},
                    name="Outliers",
                )

                return fig

        return go.Figure()  # Return empty figure if no data


def detect_outliers_zscore(data: np.ndarray, threshold: float = 3.0) -> np.ndarray:
    """Detect outliers using Z-Score method."""
    z_scores = np.abs((data - np.mean(data)) / np.std(data))
    return z_scores > threshold


def detect_outliers_iqr(data: np.ndarray) -> np.ndarray:
    """Detect outliers using Interquartile Range (IQR)."""
    q1, q3 = np.percentile(data, [25, 75])
    iqr = q3 - q1
    lower_bound = q1 - 1.5 * iqr
    upper_bound = q3 + 1.5 * iqr
    return (data < lower_bound) | (data > upper_bound)


def detect_outliers_dbscan(
    data: np.ndarray, eps: float = 0.5, min_samples: int = 5
) -> np.ndarray:
    """Detect outliers using DBSCAN clustering."""
    dbscan = DBSCAN(eps=eps, min_samples=min_samples)
    labels = dbscan.fit_predict(data.reshape(-1, 1))
    return labels == -1  # Outliers are labeled as -1


def detect_outliers_isolation_forest(data: np.ndarray) -> np.ndarray:
    """Detect outliers using Isolation Forest."""
    model = IsolationForest(contamination=0.05, random_state=42)
    model.fit(data.reshape(-1, 1))
    outliers = model.predict(data.reshape(-1, 1))
    return outliers == -1  # Outliers are labeled as -1
