import polars as pl
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from dash import Dash, Input, Output, State
from utils.store import Store


def register_correlation_heatmap_callbacks(app: "Dash") -> None:
    """Registers callbacks for generating correlation heatmaps without Pandas."""

    @app.callback(
        Output("correlation-heatmap", "figure"),  # Update correlation heatmap
        Input("file-upload-status", "data"),  # Trigger when file is uploaded
        Input("correlation-method-dropdown", "value"),  # Selected correlation method
        # prevent_initial_call=True,
    )
    def update_correlation_heatmap(file_uploaded, method):
        """Creates a correlation heatmap for numerical features based on the selected method."""
        if file_uploaded:
            df: pl.DataFrame = Store.get_static("data_frame")
            if df is not None:
                # Select only numeric columns
                numeric_columns = [
                    col for col in df.columns if df[col].dtype in (pl.Float64, pl.Int64)
                ]

                if len(numeric_columns) > 1:
                    # Convert Polars DataFrame to NumPy Array
                    data = df.select(numeric_columns).to_numpy()

                    # Compute the correlation matrix
                    if method == "pearson":
                        corr_matrix = np.corrcoef(data, rowvar=False)
                    elif method == "spearman":
                        corr_matrix = spearman_corr(data)
                    elif method == "kendall":
                        corr_matrix = kendall_corr(data)
                    else:
                        raise ValueError(f"Unsupported method: {method}")

                    # Create the heatmap with Plotly
                    fig = px.imshow(
                        corr_matrix,
                        labels=dict(color="Correlation"),
                        x=numeric_columns,
                        y=numeric_columns,
                        color_continuous_scale="RdBu_r",
                        title=f"Feature Correlation Heatmap ({method.capitalize()})",
                    )

                    return fig

        # Return an empty plot if no correlation data is available
        return go.Figure()


def spearman_corr(data: np.ndarray) -> np.ndarray:
    """Calculate Spearman correlation matrix using NumPy."""
    # Rank each column
    ranked_data = np.apply_along_axis(rank_data, axis=0, arr=data)
    # Compute Pearson correlation on ranks
    return np.corrcoef(ranked_data, rowvar=False)


def rank_data(column: np.ndarray) -> np.ndarray:
    """Compute ranks for a 1D array."""
    ranks = np.argsort(np.argsort(column))
    return ranks


def kendall_corr(data: np.ndarray) -> np.ndarray:
    """Calculate Kendall correlation matrix using NumPy."""
    n_features = data.shape[1]
    corr_matrix = np.zeros((n_features, n_features))

    for i in range(n_features):
        for j in range(i, n_features):
            x, y = data[:, i], data[:, j]
            concordant = sum(
                (x[k] - x[l]) * (y[k] - y[l]) > 0
                for k in range(len(x))
                for l in range(k + 1, len(x))
            )
            discordant = sum(
                (x[k] - x[l]) * (y[k] - y[l]) < 0
                for k in range(len(x))
                for l in range(k + 1, len(x))
            )
            corr_matrix[i, j] = corr_matrix[j, i] = (concordant - discordant) / (
                0.5 * len(x) * (len(x) - 1)
            )

    return corr_matrix
