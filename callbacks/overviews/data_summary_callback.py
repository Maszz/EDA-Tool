import dash_bootstrap_components as dbc
import polars as pl
from dash import Input, Output, dash_table, html
from scipy.stats import entropy

from utils.cache_manager import CACHE_MANAGER  # ✅ Import CacheManager
from utils.logger_config import logger  # ✅ Import logger
from utils.store import Store


def generate_summary_table(data, columns, title):
    """Generates a Dash DataTable wrapped inside a Bootstrap Card."""
    table = (
        dash_table.DataTable(
            data=data,
            columns=[{"name": col, "id": col} for col in columns],
            style_table={
                # "minHeight": "200px",
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
        if data
        else html.P("✅ No relevant data found.")
    )

    return dbc.Card(
        dbc.CardBody(
            [
                html.H5(title, className="card-title"),
                table,
            ]
        ),
        className="shadow-sm",
    )


def register_data_summary_callbacks(app) -> None:
    """Registers callbacks for displaying column data types & missing values."""

    @app.callback(
        Output("data-summary", "children"),
        Input("file-upload-status", "data"),
    )
    def render_data_summary(trigger):
        if not trigger:
            return "No dataset loaded."

        df: pl.DataFrame = Store.get_static("data_frame")
        if df is None:
            return "No dataset loaded."

        cache_key = "data_summary"
        cached_result = CACHE_MANAGER.load_cache(cache_key, df)
        if cached_result:
            return generate_summary_table(
                cached_result,
                [
                    "Column",
                    "Type",
                    "Size (KB)",
                    "Unique Values",
                    "Most Frequent Value",
                    "Zero Count",
                    "Entropy",
                    "Constant Column",
                ],
                "📌 Data Types & Column Statistics",
            )

        # Compute Data Summary
        column_types = df.schema
        column_sizes = {
            col: round(df[col].estimated_size() / 1024, 2) for col in df.columns
        }
        unique_counts = {col: int(df[col].n_unique()) for col in df.columns}
        most_frequent_values = {
            col: df[col].mode().to_list()[0] if unique_counts[col] > 1 else "-"
            for col in df.columns
        }

        summary_table_data = [
            {
                "Column": col,
                "Type": str(dtype),
                "Size (KB)": column_sizes.get(col, 0),
                "Unique Values": unique_counts[col] if dtype == pl.Utf8 else "-",
                "Most Frequent Value": (
                    most_frequent_values[col] if dtype == pl.Utf8 else "-"
                ),
                "Zero Count": (
                    int((df[col] == 0).sum())
                    if dtype in (pl.Float64, pl.Int64)
                    else "-"
                ),
                "Entropy": (
                    round(
                        entropy(df[col].value_counts().to_numpy()[:, 1].astype(float)),
                        2,
                    )
                    if dtype == pl.Utf8 and unique_counts[col] > 1
                    else "-"
                ),
                "Constant Column": "Yes" if unique_counts[col] == 1 else "No",
            }
            for col, dtype in column_types.items()
        ]
        CACHE_MANAGER.save_cache(cache_key, df, summary_table_data)
        return generate_summary_table(
            summary_table_data,
            [
                "Column",
                "Type",
                "Size (KB)",
                "Unique Values",
                "Most Frequent Value",
                "Zero Count",
                "Entropy",
                "Constant Column",
            ],
            "📌 Data Types & Column Statistics",
        )

    @app.callback(
        Output("missing-values-summary", "children"),
        Input("file-upload-status", "data"),
    )
    def render_missing_values_summary(trigger):
        if not trigger:
            return "No dataset loaded."

        df: pl.DataFrame = Store.get_static("data_frame")
        if df is None:
            return "No dataset loaded."

        cache_key = "missing_values_summary"
        cached_result = CACHE_MANAGER.load_cache(cache_key, df)
        if cached_result:
            return generate_summary_table(
                cached_result,
                ["Column", "Missing Count", "Missing %"],
                "⚠️ Missing Values Summary",
            )

        # missing_counts = df.null_count().to_dict(as_series=False)
        # missing_counts = {
        #     col: (
        #         int(missing_counts[col][0])
        #         if isinstance(missing_counts[col], list)
        #         else int(missing_counts[col])
        #     )
        #     for col in df.columns
        # }
        missing_table_data = [
            {
                "Missing Count": df[col].null_count(),
                "Column": col,
                "Missing %": f"{(df[col].null_count() / df.height * 100):.2f}%",
            }
            for col in df.columns
            if df[col].null_count() > 0
        ]

        # missing_table_data = [
        #     {
        #         "Column": col,
        #         "Missing Count": missing_counts[col],
        #         "Missing %": f"{(missing_counts[col] / df.height * 100):.2f}%",
        #     }
        #     for col in df.columns
        #     if missing_counts[col] > 0
        # ]
        CACHE_MANAGER.save_cache(cache_key, df, missing_table_data)
        return generate_summary_table(
            missing_table_data,
            ["Column", "Missing Count", "Missing %"],
            "⚠️ Missing Values Summary",
        )
