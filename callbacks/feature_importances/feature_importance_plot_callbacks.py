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
            return 2, 50, 20, {2: "2", 10: "10", 20: "20", 30: "30", 50: "50"}

        df: pl.DataFrame = Store.get_static("data_frame")
        if df is None:
            logger.error("❌ Dataset missing in memory despite upload.")
            return 2, 50, 20, {2: "2", 10: "10", 20: "20", 30: "30", 50: "50"}

        num_features = len(df.columns) - 1  # Exclude target column

        min_features = max(2, min(num_features, 2))
        max_features = min(50, num_features)
        default_features = min(20, max_features)

        num_steps = 5 if max_features > 10 else 2
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
        Input("num-top-features-slider", "value"),
        State("file-upload-status", "data"),
    )
    def update_feature_importance_plot(
        target_column, importance_method, num_top_features, file_uploaded
    ):
        """Computes and displays feature importance using LightGBM or Boruta with caching."""
        if not file_uploaded:
            return _log_and_return_empty("⚠️ No dataset loaded. Please upload a file.")

        df: pl.DataFrame = Store.get_static("data_frame")
        if df is None:
            return _log_and_return_empty("⚠️ Dataset missing in memory.")

        if not target_column:
            return _log_and_return_empty("⚠️ No target column selected.")

        cache_key = (
            f"feature_importance_{importance_method}_{target_column}_{num_top_features}"
        )
        cached_result = CACHE_MANAGER.load_cache(cache_key, df)
        if cached_result:
            importance_data = cached_result
        else:
            try:
                X_df = df.drop([target_column])
                y = df[target_column]

                num_cols = [
                    col
                    for col in X_df.columns
                    if X_df[col].dtype in (pl.Float64, pl.Int64)
                ]
                cat_cols = [col for col in X_df.columns if col not in num_cols]

                if cat_cols:
                    X_df = X_df.with_columns(
                        [
                            X_df[col].rank(descending=False).alias(col)
                            for col in cat_cols
                        ]
                    )
                    logger.info(f"📊 Encoded {len(cat_cols)} categorical features.")

                X = SimpleImputer(strategy="constant", fill_value=-999).fit_transform(
                    X_df.to_numpy()
                )
                valid_idx = ~y.is_null().to_numpy()
                X, y = X[valid_idx], y.to_numpy()[valid_idx]

                if len(y) == 0:
                    return _log_and_return_empty(
                        "⚠️ No valid target values after NaN removal."
                    )

                if df[target_column].dtype == pl.Utf8:
                    y = LabelEncoder().fit_transform(y)
                    model = lgb.LGBMClassifier(random_state=42, n_jobs=-1)
                else:
                    model = lgb.LGBMRegressor(random_state=42, n_jobs=-1)

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

                importance_data = list(zip(X_df.columns, importances))
                CACHE_MANAGER.save_cache(cache_key, df, importance_data)

            except Exception as e:
                return _log_and_return_empty(f"❌ Error: {e!s}")
        final_message = (
            f"✅ Training Completed! - Top {num_top_features} features displayed."
        )
        fig = px.bar(
            x=[imp[1] for imp in importance_data],
            y=[imp[0] for imp in importance_data],
            orientation="h",
            title=f"Feature Importance ({importance_method.upper()}) - Target: {target_column}",
            labels={"x": "Importance Score", "y": "Features"},
            template="plotly_white",
        )
        fig.update_traces(marker_color="blue", opacity=0.7)
        return fig, final_message


def _log_and_return_empty(message: str):
    logger.warning(message)
    return go.Figure(), message
