from sklearn.ensemble import RandomForestRegressor, RandomForestClassifier
from sklearn.preprocessing import LabelEncoder
import plotly.express as px
import numpy as np
import polars as pl
from dash import Dash, Input, Output, State
from utils.store import Store
import lightgbm as lgb


def register_feature_importance_callbacks(app: "Dash") -> None:
    """Registers callbacks for feature importance visualization."""

    @app.callback(
        Output("target-column", "options"),  # Populate dropdown options
        Input("file-upload-status", "data"),  # Trigger when a file is uploaded
        prevent_initial_call=True,
    )
    def update_target_dropdown(file_uploaded):
        """Populates the dropdown with available columns."""
        if file_uploaded:
            df: pl.DataFrame = Store.get_static("data_frame")
            if df is not None:
                return [{"label": col, "value": col} for col in df.columns]
        return []  # Return empty dropdown if no data

    @app.callback(
        Output("feature-importance-plot", "figure"),  # Update feature importance plot
        Input("target-column", "value"),  # Selected target column
        State("file-upload-status", "data"),  # Ensure file is uploaded
        prevent_initial_call=True,
    )
    def update_feature_importance_plot(target_column, file_uploaded):
        """Calculates and displays feature importance for the selected target column using LightGBM."""
        if file_uploaded and target_column:
            df: pl.DataFrame = Store.get_static("data_frame")
            if df is not None:
                # Separate features and target
                X_df = df.drop(
                    [df.columns[0], target_column]
                )  # Drop ID and target columns
                y = df[target_column].to_numpy()

                # Ensure all feature columns are numerical
                numerical_columns = [
                    col
                    for col in X_df.columns
                    if X_df[col].dtype in (pl.Float64, pl.Int64)
                ]
                non_numerical_columns = [
                    col for col in X_df.columns if col not in numerical_columns
                ]

                # Encode non-numerical columns
                if non_numerical_columns:
                    print(f"Encoding non-numerical columns: {non_numerical_columns}")
                    for col in non_numerical_columns:
                        X_df = X_df.with_columns(
                            X_df[col].cast(pl.Utf8).rank(descending=False).alias(col)
                        )

                # Convert X to a NumPy array
                X = X_df.to_numpy()

                # Encode target column if categorical
                if df[target_column].dtype == pl.Utf8:
                    # Target is categorical
                    le = LabelEncoder()
                    y = le.fit_transform(y)
                    model = lgb.LGBMClassifier(
                        random_state=42,
                        n_jobs=-1,
                    )
                else:
                    # Target is numerical
                    print("Numerical target detected.")
                    model = lgb.LGBMRegressor(
                        random_state=42,
                        n_jobs=-1,
                    )

                # Train the model
                print(f"Training model on features: {X.shape}, target: {y.shape}")
                model.fit(X, y)
                print("Model trained successfully.")

                # Extract feature importance
                importances = model.feature_importances_

                # Map importance to feature names and sort using Polars
                feature_names = X_df.columns
                importance_df = pl.DataFrame(
                    {"Feature": feature_names, "Importance": importances}
                ).sort("Importance", descending=True)

                # Convert to dictionary for Plotly without using Pandas
                fig = px.bar(
                    x=importance_df["Importance"].to_list(),  # Polars column to list
                    y=importance_df["Feature"].to_list(),  # Polars column to list
                    orientation="h",
                    title=f"Feature Importance (Target: {target_column})",
                    labels={"x": "Importance Score", "y": "Features"},
                    template="plotly_white",
                )

                # Customize bar chart appearance
                fig.update_traces(marker_color="blue", opacity=0.7)

                return fig

        # Return an empty plot if no target column is selected
        return px.Figure()
