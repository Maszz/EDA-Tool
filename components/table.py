import polars as pl
from dash import dash_table


def table_component(dataframe: "pl.DataFrame" = None) -> "dash_table.DataTable":
    """Generate a modern Dash DataTable from a Polars DataFrame."""
    if dataframe is None or dataframe.shape[0] == 0:
        dataframe = pl.DataFrame([{"No Data": "Upload a file to display data"}])

    return dash_table.DataTable(
        id="data-table",
        data=dataframe.to_dicts(),  # Convert first 10 rows to list of dicts
        columns=[{"name": col, "id": col} for col in dataframe.columns],
        # Table Style
        style_table={
            "overflowX": "auto",  # Scrollable table
            "borderRadius": "8px",
            "boxShadow": "0px 4px 8px rgba(0,0,0,0.1)",
            "border": "1px solid #dee2e6",
            "marginTop": "10px",
        },
        # Cell Styling
        style_cell={
            "textAlign": "left",
            "padding": "8px",
            "fontSize": "14px",
            "whiteSpace": "normal",
        },
        # Header Styling
        style_header={
            "backgroundColor": "#007bff",
            "color": "white",
            "fontWeight": "bold",
            "textAlign": "center",
            "borderBottom": "2px solid #0056b3",
        },
        # Alternate Row Styling
        style_data_conditional=[
            {
                "if": {"row_index": "odd"},
                "backgroundColor": "#f8f9fa",
            }
        ],
        page_size=10,  # Display 10 rows per page
        style_as_list_view=True,  # Removes grid lines for a cleaner look
    )
