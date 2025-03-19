import polars as pl
from dash import Input, Output

from utils.logger_config import logger  # Import logger
from utils.store import Store


def register_visualization_selector_callbacks(app) -> None:
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
        """Updates dropdowns with dataset feature lists and default selections."""
        if not file_uploaded:
            logger.warning("⚠️ No dataset uploaded. Clearing dropdowns.")
            return ([], None, [], None, [], [], [], None, [], [], [], None)

        df: pl.DataFrame = Store.get_static("data_frame")

        if df is None:
            logger.error("❌ Dataset not found in memory despite file upload.")
            return ([], None, [], None, [], [], [], None, [], [], [], None)

        try:
            # Helper function to convert column names to Dash dropdown format
            def get_dropdown_options(columns):
                return [{"label": col, "value": col} for col in columns]

            # Extract numerical and categorical features
            numeric_columns = [
                col
                for col, dtype in df.schema.items()
                if dtype in [pl.Float64, pl.Float32, pl.Int64, pl.Int32]
            ]
            categorical_columns = [
                col for col, dtype in df.schema.items() if dtype == pl.Utf8
            ]

            numeric_options = get_dropdown_options(numeric_columns)
            categorical_options = get_dropdown_options(categorical_columns)

            # Set default values
            default_x = numeric_columns[1] if numeric_columns else None
            default_y = numeric_columns[2] if len(numeric_columns) > 2 else None
            default_pairplot = numeric_columns[1:3] if len(numeric_columns) > 2 else []
            default_parallel = numeric_columns[1:3] if len(numeric_columns) > 2 else []
            default_categorical = (
                categorical_columns[0] if categorical_columns else None
            )
            default_numeric_violin = numeric_columns[1] if numeric_columns else None

            logger.info("✅ Dropdowns successfully updated with dataset features.")

            return (
                numeric_options,
                default_x,
                numeric_options,
                default_y,
                numeric_options,
                default_pairplot,
                categorical_options,
                default_categorical,
                numeric_options,
                default_parallel,
                numeric_options,
                default_numeric_violin,
            )

        except Exception as e:
            logger.error(f"❌ Error updating dropdowns: {e}")
            return ([], None, [], None, [], [], [], None, [], [], [], None)
