import polars as pl
from dash import dash_table


def table_component(dataframe: "pl.DataFrame" = None) -> "dash_table.DataTable":
    """Generate a Dash DataTable from a Pandas DataFrame."""
    if dataframe is None:
        # Initialize an empty DataFrame with no columns
        dataframe = pl.DataFrame()

    return dash_table.DataTable(
        id="data-table",
        data=dataframe.head().to_dicts(),  # Convert DataFrame to list of dicts
        columns=[{"name": col, "id": col} for col in dataframe.columns],
        style_table={"overflowX": "auto"},
        style_cell={"textAlign": "left"},
    )
