import lightgbm as lgb
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
import polars as pl
from boruta import BorutaPy
from dash import Input, Output, State
from sklearn.ensemble import RandomForestClassifier, RandomForestRegressor
from sklearn.impute import SimpleImputer
from sklearn.preprocessing import LabelEncoder

from utils.cache_manager import CACHE_MANAGER  # ✅ Import CacheManager
from utils.logger_config import logger  # ✅ Import Logger
from utils.store import Store


def register_feature_importance_plot_callbacks(app) -> None:
    """Registers callbacks for computing and visualizing feature importance with caching."""

    @app.callback(
        Output("num-top-features-slider", "min"),
        Output("num-top-features-slider", "max"),
        Output("num-top-features-slider", "value"),
        Output("num-top-features-slider", "marks"),  # ✅ Dynamic marks
        Input("file-upload-status", "data"),
    )
    def update_slider(file_uploaded):
        """Dynamically updates the slider min/max/marks based on dataset features."""
        if not file_uploaded:
            logger.warning("⚠️ No dataset uploaded. Using default slider range.")
            return (
                2,
                50,
                20,
                {2: "2", 10: "10", 20: "20", 30: "30", 50: "50"},
            )  # Default

        df: pl.DataFrame = Store.get_static("data_frame")
        if df is None:
            logger.error("❌ Dataset missing in memory despite upload.")
            return 2, 50, 20, {2: "2", 10: "10", 20: "20", 30: "30", 50: "50"}

        num_features = len(df.columns) - 1  # Exclude target column

        # ✅ Define min/max/default values
        min_features = max(2, min(num_features, 2))  # Ensure at least 2
        max_features = min(50, num_features)  # Limit max to 50 or dataset size
        default_features = min(20, max_features)  # Default selection

        # ✅ Dynamically generate marks
        num_steps = 5 if max_features > 10 else 2  # Less marks for small datasets
        marks_values = np.linspace(min_features, max_features, num_steps, dtype=int)
        marks = {int(v): str(v) for v in marks_values}

        logger.info(
            f"🔄 Updated feature slider: Min={min_features}, Max={max_features}, Default={default_features}, Marks={marks}"
        )

        return min_features, max_features, default_features, marks

    @app.callback(
        Output("feature-importance-plot", "figure"),
        Output("training-status", "children"),
        Input("target-column", "value"),
        Input("importance-method", "value"),
        Input(
            "num-top-features-slider", "value"
        ),  # ✅ NEW: User selects number of top features
        State("file-upload-status", "data"),
    )
    def update_feature_importance_plot(
        target_column, importance_method, num_top_features, file_uploaded
    ):
        """Computes and displays feature importance using LightGBM or Boruta with caching."""
        # ✅ Check if a file is uploaded
        if not file_uploaded:
            return _log_and_return_empty("⚠️ No dataset loaded. Please upload a file.")

        # ✅ Load dataset from Store
        df: pl.DataFrame = Store.get_static("data_frame")
        if df is None:
            return _log_and_return_empty("⚠️ Dataset missing in memory.")

        if not target_column:
            return _log_and_return_empty("⚠️ No target column selected.")

        # ✅ Generate a Unique Cache Key Including the Target Column
        cache_key = f"feature_importance_{importance_method}_{target_column}_{num_top_features}_{df.shape}"
        cached_result = CACHE_MANAGER.load_cache(cache_key, df)
        if cached_result:
            return cached_result  # Skip recomputation

        try:
            # ✅ Extract features and target
            X_df = df.drop([target_column])  # Drop only target column
            y = df[target_column]

            # ✅ Detect numerical and categorical columns
            num_cols = [
                col for col in X_df.columns if X_df[col].dtype in (pl.Float64, pl.Int64)
            ]
            cat_cols = [col for col in X_df.columns if col not in num_cols]

            # ✅ Encode categorical features
            if cat_cols:
                X_df = X_df.with_columns(
                    [X_df[col].rank(descending=False).alias(col) for col in cat_cols]
                )
                logger.info(f"📊 Encoded {len(cat_cols)} categorical features.")

            # ✅ Convert X to NumPy and handle missing values
            X = SimpleImputer(strategy="constant", fill_value=-999).fit_transform(
                X_df.to_numpy()
            )

            # ✅ Handle missing values in `y` (Drop NaNs)
            valid_idx = ~y.is_null().to_numpy()  # Get valid indices
            X, y = X[valid_idx], y.to_numpy()[valid_idx]  # Filter both X and y

            if len(y) == 0:
                return _log_and_return_empty(
                    "⚠️ No valid target values after NaN removal."
                )

            # ✅ Encode target for classification
            if df[target_column].dtype == pl.Utf8:
                y = LabelEncoder().fit_transform(y)
                model = lgb.LGBMClassifier(random_state=42, n_jobs=-1)
            else:
                model = lgb.LGBMRegressor(random_state=42, n_jobs=-1)

            # ✅ Compute Feature Importance
            if importance_method == "native":
                logger.info("⚙️ Training LightGBM for native feature importance...")
                model.fit(X, y)
                importances = model.feature_importances_

            elif importance_method == "boruta":
                logger.info("⚙️ Running Boruta Feature Selection...")
                rf_model = (
                    RandomForestRegressor(n_jobs=-1, random_state=42)
                    if df[target_column].dtype != pl.Utf8
                    else RandomForestClassifier(n_jobs=-1, random_state=42)
                )
                boruta_selector = BorutaPy(
                    rf_model, n_estimators="auto", verbose=0, random_state=42
                )
                boruta_selector.fit(X, y)
                importances = boruta_selector.ranking_

            # ✅ Convert to Polars DataFrame
            importance_df = pl.DataFrame(
                {"Feature": X_df.columns, "Importance": importances}
            ).sort("Importance", descending=True)

            # ✅ Apply Top `N` Filtering
            num_top_features = min(num_top_features, len(importance_df))
            importance_df = importance_df.head(num_top_features)

            # ✅ Create Plotly Bar Plot
            fig = px.bar(
                importance_df,
                x="Importance",
                y="Feature",
                orientation="h",
                title=f"Feature Importance ({importance_method.upper()}) - Target: {target_column}",
                labels={"x": "Importance Score", "y": "Features"},
                template="plotly_white",
            )
            fig.update_traces(marker_color="blue", opacity=0.7)

            final_message = (
                f"✅ Training Completed using {importance_method.capitalize()} method!"
            )

            # ✅ Save to Cache
            CACHE_MANAGER.save_cache(cache_key, df, (fig, final_message))
            logger.info("💾 Feature importance cached.")

            return fig, final_message

        except Exception as e:
            return _log_and_return_empty(f"❌ Error: {e!s}")


def _log_and_return_empty(message: str):
    """Helper function to log a warning and return an empty figure."""
    logger.warning(message)
    return go.Figure(), message
