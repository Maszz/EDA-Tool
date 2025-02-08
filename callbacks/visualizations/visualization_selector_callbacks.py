import logging
import polars as pl
from dash import Input, Output
from utils.store import Store
from utils.logger_config import logger  # Import logger


def register_visualization_selector_callbacks(app):
    """Registers callbacks for updating user selection components in the Visualization tab."""

    @app.callback(
        [
            Output("feature-x-dropdown", "options"),
            Output("feature-x-dropdown", "value"),
            Output("feature-y-dropdown", "options"),
            Output("feature-y-dropdown", "value"),
            Output("pairplot-features-dropdown", "options"),
            Output("pairplot-features-dropdown", "value"),
            Output("categorical-dropdown", "options"),
            Output("categorical-dropdown", "value"),
            Output("multivariate-features-dropdown", "options"),
            Output("multivariate-features-dropdown", "value"),
            Output("numeric-dropdown", "options"),
            Output("numeric-dropdown", "value"),
        ],
        Input("file-upload-status", "data"),
    )
    def update_visualization_selectors(file_uploaded):
        """Updates dropdowns with the feature list and sets default values."""

        if not file_uploaded:
            logger.warning("⚠️ No dataset uploaded. Clearing dropdowns.")
            return ([], None, [], None, [], [], [], None, [], [], [], None)

        df: pl.DataFrame = Store.get_static("data_frame")

        if df is None:
            logger.error("❌ Dataset not found in memory despite file upload.")
            return ([], None, [], None, [], [], [], None, [], [], [], None)

        try:
            # Extract numerical and categorical features
            numeric_features = [
                {"label": col, "value": col}
                for col in df.columns
                if df[col].dtype in [pl.Float64, pl.Float32, pl.Int64, pl.Int32]
            ]
            categorical_features = [
                {"label": col, "value": col}
                for col in df.columns
                if df[col].dtype == pl.Utf8
            ]

            # Default selections
            default_x = numeric_features[0]["value"] if numeric_features else None
            default_y = (
                numeric_features[1]["value"] if len(numeric_features) > 1 else None
            )
            default_pairplot = [feature["value"] for feature in numeric_features]
            default_parallel = [feature["value"] for feature in numeric_features]
            default_categorical = (
                categorical_features[0]["value"] if categorical_features else None
            )
            default_numeric_violin = (
                numeric_features[0]["value"] if numeric_features else None
            )

            logger.info("✅ Dropdowns updated successfully with dataset features.")

            return (
                numeric_features,
                default_x,
                numeric_features,
                default_y,
                numeric_features,
                default_pairplot,
                categorical_features,
                default_categorical,
                numeric_features,
                default_parallel,
                numeric_features,
                default_numeric_violin,
            )

        except Exception as e:
            logger.error(f"❌ Error updating dropdowns: {e}")
            return ([], None, [], None, [], [], [], None, [], [], [], None)
