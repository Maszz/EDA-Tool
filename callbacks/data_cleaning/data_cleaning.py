from dash import Input, Output, State, callback, html, ctx, dcc
import polars as pl
import numpy as np
from utils.logger_config import logger
from utils.store import Store
from callbacks.overviews.data_summary_callback import generate_summary_table
import io
import base64
from typing import Optional, Dict, Any, Tuple

store = Store()


def handle_missing_values(df: pl.DataFrame, column: str, method: str) -> pl.DataFrame:
    """Handle missing values in the specified column using the given method."""
    if method == "mean":
        return df.with_columns(pl.col(column).fill_null(pl.col(column).mean()))
    elif method == "median":
        return df.with_columns(pl.col(column).fill_null(pl.col(column).median()))
    elif method == "mode":
        return df.with_columns(pl.col(column).fill_null(pl.col(column).mode().first()))
    elif method == "drop":
        return df.drop_nulls(subset=[column])
    else:
        raise ValueError(f"Unsupported missing value treatment method: {method}")


def convert_data_type(df: pl.DataFrame, column: str, target_type: str) -> pl.DataFrame:
    """Convert the data type of the specified column."""
    try:
        return df.with_columns(pl.col(column).cast(getattr(pl, target_type)))
    except Exception as e:
        raise ValueError(f"Error converting {column} to {target_type}: {str(e)}")


def create_preview_data(
    df: pl.DataFrame, rows: int = 5
) -> tuple[list[Dict[str, Any]], list[str]]:
    """Create preview data for the table display."""
    preview_df = df.head(rows)
    preview_data = [
        {col: preview_df[i][col].to_list()[0] for col in preview_df.columns}
        for i in range(len(preview_df))
    ]
    return preview_data, list(preview_df.columns)


def register_data_cleaning_callbacks(app):
    """Register all callbacks for the data cleaning page."""

    @app.callback(
        [
            Output("cleaned-data-preview", "children"),
            Output(
                "data-cleaning-trigger", "data"
            ),  # New output to trigger dropdown update
        ],
        [
            Input("apply-missing-treatment", "n_clicks"),
            Input("convert-type", "n_clicks"),
            Input("remove-duplicates", "n_clicks"),
        ],
        [
            State("column-select-missing", "value"),
            State("missing-treatment-method", "value"),
            State("column-select-type", "value"),
            State("type-conversion", "value"),
            State("file-upload-status", "data"),
        ],
    )
    def update_cleaned_data(
        missing_clicks: Optional[int],
        type_clicks: Optional[int],
        duplicate_clicks: Optional[int],
        missing_col: Optional[str],
        missing_method: Optional[str],
        type_col: Optional[str],
        type_method: Optional[str],
        file_uploaded: bool,
    ) -> Tuple[html.Div, bool]:
        """Update the cleaned data preview based on user actions."""
        if not file_uploaded:
            logger.warning("⚠️ No dataset available for cleaning.")
            return "Please upload a dataset first.", False

        df: Optional[pl.DataFrame] = Store.get_static("data_frame")
        if df is None:
            logger.warning("⚠️ Dataset not found in memory.")
            return "Dataset not found in memory.", False

        ctx_id = ctx.triggered_id

        try:
            if ctx_id == "apply-missing-treatment":
                if missing_col and missing_method:
                    if missing_col is None:  # No missing values found
                        return "No missing values to treat.", False
                    logger.info(
                        f"🧹 Applying {missing_method} treatment to {missing_col}"
                    )
                    df = handle_missing_values(df, missing_col, missing_method)

            elif ctx_id == "convert-type":
                if type_col and type_method:
                    logger.info(f"🔄 Converting {type_col} to {type_method}")
                    df = convert_data_type(df, type_col, type_method)
                    logger.info(
                        f"✅ Successfully converted {type_col} to {type_method}"
                    )

            elif ctx_id == "remove-duplicates":
                logger.info("🧹 Removing duplicate rows")
                df = df.unique()
                logger.info("✅ Duplicate rows removed successfully")

            # Update the store with cleaned data
            store.set("data_frame", df)
            logger.info("✅ Data cleaning completed successfully.")

            # Create preview data for the table
            preview_data, columns = create_preview_data(df)
            return (
                generate_summary_table(
                    preview_data, columns, "🧹 Cleaned Data Preview"
                ),
                True,
            )  # Trigger dropdown update

        except Exception as e:
            logger.error(f"❌ Error during data cleaning: {str(e)}")
            return f"Error: {str(e)}", False

    @app.callback(
        Output("download-dataframe-csv", "data"),
        Input("download-cleaned-data", "n_clicks"),
        prevent_initial_call=True,
    )
    def download_dataframe(n_clicks: Optional[int]) -> Optional[Dict[str, Any]]:
        """Handle the download of cleaned data as CSV."""
        if not n_clicks:
            return None

        df: Optional[pl.DataFrame] = Store.get_static("data_frame")
        if df is None:
            logger.warning("⚠️ No dataset available for download.")
            return None

        try:
            # Convert to CSV
            csv_buffer = io.StringIO()
            df.write_csv(csv_buffer)
            csv_str = csv_buffer.getvalue()

            # Create download
            return dcc.send_bytes(
                csv_str.encode("utf-8"),
                "cleaned_data.csv",
                "text/csv",
                base64=True,
            )
        except Exception as e:
            logger.error(f"❌ Error during data download: {str(e)}")
            return None
