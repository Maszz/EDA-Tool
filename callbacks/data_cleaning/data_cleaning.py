from dash import Input, Output, State, callback, html, ctx, dcc
import polars as pl
import numpy as np
from utils.logger_config import logger
from utils.store import Store
from callbacks.overviews.data_summary_callback import generate_summary_table
import io
import base64

store = Store()


def register_data_cleaning_callbacks(app):
    """Register all callbacks for the data cleaning page."""

    @app.callback(
        Output("cleaned-data-preview", "children"),
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
        missing_clicks,
        type_clicks,
        duplicate_clicks,
        missing_col,
        missing_method,
        type_col,
        type_method,
        file_uploaded,
    ):
        if not file_uploaded:
            logger.warning("⚠️ No dataset available for cleaning.")
            return "Please upload a dataset first."

        df: pl.DataFrame = Store.get_static("data_frame")
        if df is None:
            logger.warning("⚠️ Dataset not found in memory.")
            return "Dataset not found in memory."

        ctx_id = ctx.triggered_id

        if ctx_id == "apply-missing-treatment":
            if missing_col and missing_method:
                if missing_col is None:  # No missing values found
                    return "No missing values to treat."
                logger.info(f"🧹 Applying {missing_method} treatment to {missing_col}")
                if missing_method == "mean":
                    df = df.with_columns(
                        pl.col(missing_col).fill_null(pl.col(missing_col).mean())
                    )
                elif missing_method == "median":
                    df = df.with_columns(
                        pl.col(missing_col).fill_null(pl.col(missing_col).median())
                    )
                elif missing_method == "mode":
                    df = df.with_columns(
                        pl.col(missing_col).fill_null(
                            pl.col(missing_col).mode().first()
                        )
                    )
                elif missing_method == "drop":
                    df = df.drop_nulls(subset=[missing_col])

        elif ctx_id == "convert-type":
            if type_col and type_method:
                logger.info(f"🔄 Converting {type_col} to {type_method}")
                try:
                    df = df.with_columns(
                        pl.col(type_col).cast(getattr(pl, type_method))
                    )
                    logger.info(
                        f"✅ Successfully converted {type_col} to {type_method}"
                    )
                except Exception as e:
                    logger.error(
                        f"❌ Error converting {type_col} to {type_method}: {str(e)}"
                    )
                    return f"Error converting column: {str(e)}"

        elif ctx_id == "remove-duplicates":
            logger.info("🧹 Removing duplicate rows")
            df = df.unique()
            logger.info("✅ Duplicate rows removed successfully")

        # Update the store with cleaned data
        store.set("data_frame", df)
        logger.info("✅ Data cleaning completed successfully.")

        # Create preview data for the table
        preview_df = df.head(5)
        preview_data = [
            {col: preview_df[i][col].to_list()[0] for col in preview_df.columns}
            for i in range(len(preview_df))
        ]
        columns = list(preview_df.columns)

        return generate_summary_table(preview_data, columns, "🧹 Cleaned Data Preview")

    @app.callback(
        Output("download-dataframe-csv", "data"),
        Input("download-cleaned-data", "n_clicks"),
        prevent_initial_call=True,
    )
    def download_dataframe(n_clicks):
        if not n_clicks:
            return None

        df: pl.DataFrame = Store.get_static("data_frame")
        if df is None:
            logger.warning("⚠️ No dataset available for download.")
            return None

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
