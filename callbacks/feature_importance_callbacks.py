from sklearn.preprocessing import LabelEncoder
import plotly.express as px
import polars as pl
from dash import Dash, Input, Output, State, ctx
from utils.store import Store
import lightgbm as lgb
import plotly.graph_objects as go
from dash import dcc
from boruta import BorutaPy
from sklearn.ensemble import RandomForestRegressor, RandomForestClassifier
from sklearn.impute import SimpleImputer


def register_feature_importance_callbacks(app: "Dash") -> None:
    """Registers callbacks for feature importance visualization."""

    @app.callback(
        Output("target-column", "options"),  # Populate dropdown options
        Output(
            "training-status", "children", allow_duplicate=True
        ),  # Update training status
        Input("file-upload-status", "data"),  # Trigger when a file is uploaded
        Input("target-column", "value"),  # Trigger when a new target column is selected
        Input("importance-method", "value"),  # Trigger when importance method changes
    )
    def update_target_dropdown(file_uploaded, target_column, importance_method):
        """Populates the dropdown with available columns and updates training status."""
        ctx_id = ctx.triggered_id  # Identify which input triggered callback

        if file_uploaded:
            df: pl.DataFrame = Store.get_static("data_frame")
            if df is not None:
                options = [{"label": col, "value": col} for col in df.columns[1::]]

                # If triggered by file upload, inform the user that a target must be selected
                if ctx_id == "file-upload-status":
                    return options, "⚠️ No target column selected."

                # If a target is selected, show training in progress message
                if ctx_id in ["target-column", "importance-method"]:
                    return options, "⏳ Training in Progress... Please wait."

                return options, ""

        return [], ""  # Return empty dropdown if no data

    @app.callback(
        Output("feature-importance-plot", "figure"),
        Output("training-status", "children"),
        Input("target-column", "value"),
        Input("importance-method", "value"),
        State("file-upload-status", "data"),
    )
    def update_feature_importance_plot(target_column, importance_method, file_uploaded):
        """Calculates and displays feature importance for the selected target column using LightGBM or Boruta."""
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
                    for col in non_numerical_columns:
                        X_df = X_df.with_columns(
                            X_df[col].cast(pl.Utf8).rank(descending=False).alias(col)
                        )

                # Convert X to a NumPy array
                X = X_df.to_numpy()

                # Handle missing values in X (like LightGBM)
                imputer_X = SimpleImputer(strategy="constant", fill_value=-999)
                X = imputer_X.fit_transform(X)

                # Handle missing values in y
                if df[target_column].dtype == pl.Utf8:
                    # Categorical target: Fill NaNs before encoding
                    imputer_y = SimpleImputer(strategy="most_frequent")
                    y = imputer_y.fit_transform(y.reshape(-1, 1)).ravel()

                    # Encode categorical target
                    le = LabelEncoder()
                    y = le.fit_transform(y)
                    model = lgb.LGBMClassifier(random_state=42, n_jobs=-1)
                else:
                    # Numerical target: Fill NaNs
                    imputer_y = SimpleImputer(strategy="mean")
                    y = imputer_y.fit_transform(y.reshape(-1, 1)).ravel()
                    model = lgb.LGBMRegressor(random_state=42, n_jobs=-1)

                if importance_method == "native":
                    # Train the LightGBM model
                    model.fit(X, y)
                    importances = model.feature_importances_

                elif importance_method == "boruta":
                    # Use BorutaPy for feature selection
                    print("🔍 Running Boruta Feature Selection...")
                    rf_model = (
                        RandomForestRegressor(n_jobs=-1, random_state=42)
                        if df[target_column].dtype != pl.Utf8
                        else RandomForestClassifier(n_jobs=-1, random_state=42)
                    )

                    # Ensure RandomForest receives same preprocessed data
                    boruta_selector = BorutaPy(
                        rf_model,
                        n_estimators="auto",
                        verbose=2,
                        random_state=42,
                    )

                    # Fit Boruta selector
                    boruta_selector.fit(X, y)

                    # Get selected feature importances
                    importances = boruta_selector.ranking_

                # Map importance to feature names and sort using Polars
                feature_names = X_df.columns
                importance_df = pl.DataFrame(
                    {"Feature": feature_names, "Importance": importances}
                ).sort("Importance", descending=True)

                # Create bar plot
                fig = px.bar(
                    x=importance_df["Importance"].to_list(),
                    y=importance_df["Feature"].to_list(),
                    orientation="h",
                    title=f"Feature Importance ({importance_method.upper()}) - Target: {target_column}",
                    labels={"x": "Importance Score", "y": "Features"},
                    template="plotly_white",
                )
                fig.update_traces(marker_color="blue", opacity=0.7)

                # Update final message
                final_message = f"✅ Training Completed using {importance_method.capitalize()} method! Feature Importance is now displayed."

                return fig, final_message

        # Return an empty plot if no target column is selected
        if not file_uploaded:
            return go.Figure(), ""

        return go.Figure(), "⚠️ No target column selected."
