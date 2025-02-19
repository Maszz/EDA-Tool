import dash_bootstrap_components as dbc
import polars as pl
from dash import Input, Output, dash_table, html
from scipy.stats import entropy

from utils.cache_manager import CACHE_MANAGER  # ✅ Import CacheManager
from utils.logger_config import logger  # ✅ Import logger
from utils.store import Store


def register_data_summary_callbacks(app) -> None:
    """Registers callbacks for displaying column data types & missing values in a single table."""

    @app.callback(
        Output("data-summary", "children"),
        Input("file-upload-status", "data"),
    )
    def render_data_summary(trigger):
        """Displays column statistics including size, dtype, unique values, and distribution info."""
        if not trigger:
            return "No dataset loaded."

        df: pl.DataFrame = Store.get_static("data_frame")
        if df is None:
            return "No dataset loaded."

        # ✅ Generate a unique cache key based on dataset shape
        cache_key = f"data_summary"
        cached_result = CACHE_MANAGER.load_cache(cache_key, df)
        if cached_result:
            return cached_result  # ✅ Return cached result instantly

        # ✅ Compute Data Summary Efficiently
        total_rows = df.height
        column_types = df.schema  # ✅ Extract column names & data types
        column_sizes = {
            col: round(df[col].estimated_size() / 1024, 2) for col in df.columns
        }  # Convert to KB

        unique_counts = {
            col: int(df[col].n_unique()) for col in df.columns
        }  # ✅ Count unique values
        most_frequent_values = {
            col: df[col].mode().to_list()[0] if unique_counts[col] > 1 else "-"
            for col in df.columns
        }  # ✅ Retrieve most frequent value

        total_size_kb = sum(column_sizes.values())  # ✅ Compute total dataset size

        logger.info(f"📊 Data Summary: {len(column_types)} columns, {total_rows} rows.")
        logger.info(f"💾 Total Dataset Size: {total_size_kb:.2f} KB")

        summary_table_data = []
        for col, dtype in column_types.items():
            col_size_kb = column_sizes.get(col, 0)
            unique_count = unique_counts.get(col, 0)
            most_frequent = most_frequent_values.get(col, "-")
            zero_count = (
                int((df[col] == 0).sum()) if dtype in (pl.Float64, pl.Int64) else "-"
            )

            # ✅ Compute entropy only for categorical columns with multiple values
            if dtype == pl.Utf8 and unique_count > 1:
                counts = (
                    df[col].value_counts().to_numpy()[:, 1].astype(float)
                )  # Convert to numeric counts
                entropy_value = (
                    round(entropy(counts), 2) if counts.sum() > 0 else 0
                )  # Compute entropy safely
            else:
                entropy_value = "-"

            is_constant = "Yes" if unique_count == 1 else "No"

            col_stats = {
                "Column": col,
                "Type": str(dtype),
                "Size (KB)": col_size_kb,
                "Unique Values": unique_count if dtype == pl.Utf8 else "-",
                "Most Frequent Value": most_frequent if dtype == pl.Utf8 else "-",
                "Zero Count": zero_count,
                "Entropy": entropy_value if dtype == pl.Utf8 else "-",
                "Constant Column": is_constant,
            }

            summary_table_data.append(col_stats)

        # ✅ Create Dash Table for Display
        summary_table = dash_table.DataTable(
            data=summary_table_data,
            columns=[
                {"name": "Column", "id": "Column"},
                {"name": "Type", "id": "Type"},
                {"name": "Size (KB)", "id": "Size (KB)"},
                {"name": "Unique Values", "id": "Unique Values"},
                {"name": "Most Frequent Value", "id": "Most Frequent Value"},
                {"name": "Zero Count", "id": "Zero Count"},
                {"name": "Entropy", "id": "Entropy"},
                {"name": "Constant Column", "id": "Constant Column"},
            ],
            style_table={
                "maxHeight": "400px",
                "overflowY": "auto",
                "borderRadius": "8px",
                "boxShadow": "0px 4px 8px rgba(0,0,0,0.1)",
                "border": "1px solid #dee2e6",
            },
            page_size=10,
            virtualization=True,
            style_cell={
                "textAlign": "left",
                "padding": "8px",
                "fontSize": "14px",
                "whiteSpace": "normal",
            },
            style_header={
                "backgroundColor": "#007bff",
                "color": "white",
                "fontWeight": "bold",
            },
            style_data_conditional=[
                {"if": {"row_index": "odd"}, "backgroundColor": "#f8f9fa"}
            ],
        )

        logger.info("✅ Data summary table successfully generated.")

        # ✅ Store computed summary in cache
        result = dbc.Card(
            dbc.CardBody(
                [
                    html.H5(
                        "📌 Data Types & Column Statistics", className="card-title"
                    ),
                    summary_table,
                ]
            ),
            className="shadow-sm",
        )

        CACHE_MANAGER.save_cache(cache_key, df, result)
        logger.info("💾 Cached data summary for future use.")

        return result

    @app.callback(
        Output("missing-values-summary", "children"),
        Input("file-upload-status", "data"),
    )
    def render_missing_values_summary(trigger):
        """Displays missing values summary using Polars with caching."""
        if not trigger:
            return "No dataset loaded."

        df: pl.DataFrame = Store.get_static("data_frame")
        if df is None:
            return "No dataset loaded."

        # ✅ Generate unique cache key based on dataset shape
        cache_key = f"missing_values_summary"
        cached_result = CACHE_MANAGER.load_cache(cache_key, df)
        if cached_result:
            return cached_result  # ✅ Return cached result instantly

        # ✅ Compute missing values efficiently
        total_rows = df.height
        missing_counts = df.null_count().to_dict(as_series=False)

        # ✅ Extract integer values from lists (Fix TypeError)
        missing_counts = {
            col: (
                int(missing_counts[col][0])
                if isinstance(missing_counts[col], list)
                else int(missing_counts[col])
            )
            for col in df.columns
        }

        # ✅ Compute total missing values
        total_missing = sum(missing_counts.values())

        logger.info(f"⚠️ Total Missing Values: {total_missing} entries detected.")

        # ✅ Create Summary Table Data
        missing_table_data = [
            {
                "Column": col,
                "Missing Count": missing_counts[col],
                "Missing %": (
                    f"{(missing_counts[col] / total_rows * 100):.2f}%"
                    if total_rows > 0
                    else "0.00%"
                ),
            }
            for col in df.columns
            if missing_counts[col] > 0  # ✅ Only show columns with missing data
        ]

        missing_table = (
            dash_table.DataTable(
                data=missing_table_data,
                columns=[
                    {"name": "Column", "id": "Column"},
                    {"name": "Missing Count", "id": "Missing Count"},
                    {"name": "Missing %", "id": "Missing %"},
                ],
                style_table={
                    "maxHeight": "400px",
                    "overflowY": "auto",
                    "borderRadius": "8px",
                    "boxShadow": "0px 4px 8px rgba(0,0,0,0.1)",
                    "border": "1px solid #dee2e6",
                },
                page_size=10,
                virtualization=True,
                style_cell={
                    "textAlign": "left",
                    "padding": "8px",
                    "fontSize": "14px",
                    "whiteSpace": "normal",
                },
                style_header={
                    "backgroundColor": "#007bff",
                    "color": "white",
                    "fontWeight": "bold",
                },
                style_data_conditional=[
                    {"if": {"row_index": "odd"}, "backgroundColor": "#f8f9fa"}
                ],
            )
            if missing_table_data
            else html.P("✅ No missing values found.")
        )

        logger.info("✅ Missing values summary table successfully generated.")

        # ✅ Store computed summary in cache
        result = dbc.Card(
            dbc.CardBody(
                [
                    html.H5("⚠️ Missing Values Summary", className="card-title"),
                    missing_table,
                ]
            ),
            className="shadow-sm",
        )

        CACHE_MANAGER.save_cache(cache_key, df, result)
        logger.info("💾 Cached missing values summary for future use.")

        return result
