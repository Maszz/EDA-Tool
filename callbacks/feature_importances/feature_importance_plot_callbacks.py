import polars as pl
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from dash import Input, Output, State
from utils.store import Store
from utils.logger_config import logger  # Import logger
import lightgbm as lgb
from boruta import BorutaPy
from sklearn.ensemble import RandomForestRegressor, RandomForestClassifier
from sklearn.impute import SimpleImputer
from sklearn.preprocessing import LabelEncoder


def register_feature_importance_plot_callbacks(app):
    """Registers callbacks for computing and visualizing feature importance."""

    @app.callback(
        Output("feature-importance-plot", "figure"),
        Output("training-status", "children"),
        Input("target-column", "value"),
        Input("importance-method", "value"),
        State("file-upload-status", "data"),
    )
    def update_feature_importance_plot(target_column, importance_method, file_uploaded):
        """Computes and displays feature importance for the selected target column using LightGBM or Boruta."""

        # ✅ Check if a file is uploaded
        if not file_uploaded:
            logger.warning("⚠️ No file uploaded. Feature importance cannot be computed.")
            return go.Figure(), "⚠️ No dataset loaded. Please upload a file."

        # ✅ Load dataset from Store
        df: pl.DataFrame = Store.get_static("data_frame")
        if df is None:
            logger.error(
                "❌ Dataset missing in memory despite upload. Possible storage issue."
            )
            return go.Figure(), "⚠️ Dataset not found in memory. Please re-upload."

        if not target_column:
            logger.warning("⚠️ No target column selected for feature importance.")
            return go.Figure(), "⚠️ No target column selected."

        try:
            # Separate features and target
            X_df = df.drop([df.columns[0], target_column])  # Drop ID and target columns
            y = df[target_column].to_numpy()

            # Identify numerical and non-numerical columns
            numerical_columns = [
                col for col in X_df.columns if X_df[col].dtype in (pl.Float64, pl.Int64)
            ]
            non_numerical_columns = [
                col for col in X_df.columns if col not in numerical_columns
            ]

            # Encode categorical columns
            if non_numerical_columns:
                for col in non_numerical_columns:
                    X_df = X_df.with_columns(
                        X_df[col].cast(pl.Utf8).rank(descending=False).alias(col)
                    )
                logger.info(
                    f"📊 Encoded {len(non_numerical_columns)} categorical features."
                )

            # Convert X to a NumPy array
            X = X_df.to_numpy()

            # Handle missing values
            imputer_X = SimpleImputer(strategy="constant", fill_value=-999)
            X = imputer_X.fit_transform(X)

            # Select Model Based on Target Type
            if df[target_column].dtype == pl.Utf8:
                imputer_y = SimpleImputer(strategy="most_frequent")
                y = imputer_y.fit_transform(y.reshape(-1, 1)).ravel()

                le = LabelEncoder()
                y = le.fit_transform(y)

                model = lgb.LGBMClassifier(random_state=42, n_jobs=-1)
                logger.info(f"🟢 Using LightGBM Classifier for target: {target_column}")

            else:
                imputer_y = SimpleImputer(strategy="mean")
                y = imputer_y.fit_transform(y.reshape(-1, 1)).ravel()

                model = lgb.LGBMRegressor(random_state=42, n_jobs=-1)
                logger.info(f"🟠 Using LightGBM Regressor for target: {target_column}")

            # Compute Feature Importance
            if importance_method == "native":
                logger.info(
                    f"⚙️ Training LightGBM model with native importance method..."
                )
                model.fit(X, y)
                importances = model.feature_importances_
                logger.info("✅ Feature importance computed using LightGBM.")

            elif importance_method == "boruta":
                logger.info(f"⚙️ Running Boruta Feature Selection...")
                rf_model = (
                    RandomForestRegressor(n_jobs=-1, random_state=42)
                    if df[target_column].dtype != pl.Utf8
                    else RandomForestClassifier(n_jobs=-1, random_state=42)
                )

                boruta_selector = BorutaPy(
                    rf_model, n_estimators="auto", verbose=2, random_state=42
                )
                boruta_selector.fit(X, y)
                importances = boruta_selector.ranking_
                logger.info("✅ Feature importance computed using Boruta.")

            # Convert Feature Importance to Polars DataFrame
            feature_names = X_df.columns
            importance_df = pl.DataFrame(
                {"Feature": feature_names, "Importance": importances}
            ).sort("Importance", descending=True)

            # Create Bar Plot
            fig = px.bar(
                x=importance_df["Importance"].to_list(),
                y=importance_df["Feature"].to_list(),
                orientation="h",
                title=f"Feature Importance ({importance_method.upper()}) - Target: {target_column}",
                labels={"x": "Importance Score", "y": "Features"},
                template="plotly_white",
            )
            fig.update_traces(marker_color="blue", opacity=0.7)

            final_message = f"✅ Training Completed using {importance_method.capitalize()} method! Feature Importance is now displayed."
            return fig, final_message

        except Exception as e:
            logger.error(f"❌ Error in feature importance computation: {e}")
            return go.Figure(), f"❌ Error: {str(e)}"
