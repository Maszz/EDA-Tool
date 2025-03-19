import polars as pl
from dash import Input, Output, ctx, State
from utils.logger_config import logger
from utils.store import Store


def register_data_cleaning_selector_callbacks(app) -> None:
    """Registers callbacks for selecting columns in data cleaning page."""

    @app.callback(
        [
            Output("column-select-missing", "options"),
            Output("column-select-type", "options"),
            Output("duplicate-info", "children"),
            Output("apply-missing-treatment", "disabled"),
            Output("convert-type", "disabled"),
            Output("remove-duplicates", "disabled"),
            Output("download-cleaned-data", "disabled"),
        ],
        Input("file-upload-status", "data"),
    )
    def update_column_dropdowns(file_uploaded):
        """Populates the dropdowns with available columns."""
        if not file_uploaded:
            logger.warning("⚠️ No file uploaded. Cannot populate column dropdowns.")
            return [], [], "Please upload a dataset first.", True, True, True, True

        df: pl.DataFrame = Store.get_static("data_frame")

        if df is None:
            logger.warning(
                "⚠️ No dataset in memory despite file upload. Possible storage issue."
            )
            return [], [], "Dataset not found in memory.", True, True, True, True

        # Get all column names for type conversion
        all_columns = [{"label": col, "value": col} for col in df.columns]

        # Get columns with missing values and their counts
        missing_columns = [
            {
                "label": f"{col} ({df[col].null_count()} rows)",
                "value": col,
            }
            for col in df.columns
            if df[col].null_count() > 0
        ]

        # Check for duplicate rows
        duplicate_count = df.height - df.unique().height
        if duplicate_count > 0:
            duplicate_info = f"Found {duplicate_count} duplicate rows"
            remove_duplicates_disabled = False
        else:
            duplicate_info = "No duplicate rows found"
            remove_duplicates_disabled = True

        # Add message if no missing values
        if not missing_columns:
            missing_columns = [{"label": "No missing values found", "value": None}]

        logger.info("✅ Column dropdowns updated successfully.")
        return (
            missing_columns,
            all_columns,
            duplicate_info,
            False,
            False,
            remove_duplicates_disabled,
            False,
        )

    @app.callback(
        Output("type-conversion", "options"),
        Input("column-select-type", "value"),
        State("file-upload-status", "data"),
    )
    def update_type_conversion_options(selected_column, file_uploaded):
        """Updates type conversion options based on selected column's data type."""
        if not file_uploaded or not selected_column:
            return []

        df: pl.DataFrame = Store.get_static("data_frame")
        if df is None:
            return []

        # Get the data type of the selected column
        col_type = df[selected_column].dtype

        # Define conversion options based on current type
        if col_type in [pl.Float64, pl.Float32, pl.Int64, pl.Int32, pl.Int16, pl.Int8]:
            return [
                {"label": "Float64", "value": "Float64"},
                {"label": "Float32", "value": "Float32"},
                {"label": "Int64", "value": "Int64"},
                {"label": "Int32", "value": "Int32"},
                {"label": "Int16", "value": "Int16"},
                {"label": "Int8", "value": "Int8"},
            ]
        elif col_type == pl.Categorical:
            return [
                {"label": "String", "value": "String"},
                {"label": "Categorical", "value": "Categorical"},
            ]
        elif col_type == pl.String:
            return [
                {"label": "String", "value": "String"},
                {"label": "Categorical", "value": "Categorical"},
            ]
        elif col_type == pl.Datetime:
            return [
                {"label": "Datetime", "value": "Datetime"},
                {"label": "Date", "value": "Date"},
            ]
        else:
            return [
                {"label": "String", "value": "String"},
                {"label": "Categorical", "value": "Categorical"},
            ]
