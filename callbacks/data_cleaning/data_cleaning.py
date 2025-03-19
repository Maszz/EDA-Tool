from dash import Input, Output, State, callback, html
import polars as pl
import numpy as np
from utils.logger_config import logger
from utils.store import Store

store = Store()


def register_data_cleaning_callbacks(app):
    """Register all callbacks for the data cleaning page."""

    @app.callback(
        Output("cleaned-data-preview", "children"),
        [
            Input("apply-missing-treatment", "n_clicks"),
            Input("detect-outliers", "n_clicks"),
            Input("convert-type", "n_clicks"),
            Input("remove-duplicates", "n_clicks"),
        ],
        [
            State("column-select-missing", "value"),
            State("missing-treatment-method", "value"),
            State("column-select-outlier", "value"),
            State("outlier-method", "value"),
            State("column-select-type", "value"),
            State("type-conversion", "value"),
            State("duplicate-columns", "value"),
            State("file-upload-status", "data"),
        ],
    )
    def update_cleaned_data(
        missing_clicks,
        outlier_clicks,
        type_clicks,
        duplicate_clicks,
        missing_col,
        missing_method,
        outlier_col,
        outlier_method,
        type_col,
        type_method,
        duplicate_cols,
        file_uploaded,
    ):
        if not file_uploaded:
            logger.warning("⚠️ No dataset available for cleaning.")
            return "Please upload a dataset first."

        df: pl.DataFrame = Store.get_static("data_frame")
        if df is None:
            logger.warning("⚠️ Dataset not found in memory.")
            return "Dataset not found in memory."

        ctx = callback.triggered[0]

        if ctx["prop_id"] == "apply-missing-treatment.n_clicks":
            if missing_col and missing_method:
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

        elif ctx["prop_id"] == "detect-outliers.n_clicks":
            if outlier_col and outlier_method:
                logger.info(
                    f"🔍 Detecting outliers in {outlier_col} using {outlier_method}"
                )
                if outlier_method == "iqr":
                    Q1 = df[outlier_col].quantile(0.25)
                    Q3 = df[outlier_col].quantile(0.75)
                    IQR = Q3 - Q1
                    df = df.filter(
                        ~(
                            (pl.col(outlier_col) < (Q1 - 1.5 * IQR))
                            | (pl.col(outlier_col) > (Q3 + 1.5 * IQR))
                        )
                    )
                elif outlier_method == "zscore":
                    z_scores = (
                        (pl.col(outlier_col) - pl.col(outlier_col).mean())
                        / pl.col(outlier_col).std()
                    ).abs()
                    df = df.filter(z_scores < 3)

        elif ctx["prop_id"] == "convert-type.n_clicks":
            if type_col and type_method:
                logger.info(f"🔄 Converting {type_col} to {type_method}")
                if type_method == "numeric":
                    df = df.with_columns(pl.col(type_col).cast(pl.Float64))
                elif type_method == "categorical":
                    df = df.with_columns(pl.col(type_col).cast(pl.Categorical))
                elif type_method == "date":
                    df = df.with_columns(pl.col(type_col).cast(pl.Datetime))

        elif ctx["prop_id"] == "remove-duplicates.n_clicks":
            if duplicate_cols:
                logger.info(
                    f"🧹 Removing duplicates based on columns: {duplicate_cols}"
                )
                df = df.unique(subset=duplicate_cols)

        # Update the store with cleaned data
        store.update("data_frame", df)
        logger.info("✅ Data cleaning completed successfully.")

        # Create a table preview of the cleaned data
        preview_df = df.head(5)
        return html.Table(
            [
                html.Thead(html.Tr([html.Th(col) for col in preview_df.columns])),
                html.Tbody(
                    [
                        html.Tr(
                            [html.Td(preview_df[i][col]) for col in preview_df.columns]
                        )
                        for i in range(len(preview_df))
                    ]
                ),
            ],
            className="table table-striped table-bordered",
        )
