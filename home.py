# import dash
# from dash import html, dcc

# from components.upload import upload_component
# import dash_bootstrap_components as dbc

# dash.register_page(__name__, path="/", title="Home")


# def layout(**kwargs: dict[str, str]) -> "html.Div":
#     return dbc.Container(
#         [
#             # Title Section
#             html.Div(
#                 [
#                     html.H1("📊 Exploratory Data Analysis Tool", className="display-4"),
#                     html.P(
#                         "A simple yet powerful tool to explore your datasets.",
#                         className="lead text-muted",
#                     ),
#                 ],
#                 className="text-center my-4",
#             ),
#             # Upload Section
#             dbc.Row(
#                 [
#                     dbc.Col(upload_component(), width=6),
#                 ],
#                 className="justify-content-center mb-4",
#             ),
#             # Tabs for EDA Sections
#             dbc.Tabs(
#                 [
#                     # Data Overview Tab
#                     dbc.Tab(
#                         label="📋 Data Overview",
#                         tab_id="tab-overview",
#                         children=[
#                             dbc.Row(
#                                 [
#                                     dbc.Col(
#                                         dbc.Card(
#                                             [
#                                                 dbc.CardHeader(
#                                                     "Top 10 Record Preview",
#                                                     className="bg-primary text-white",
#                                                 ),
#                                                 dbc.CardBody(
#                                                     html.Div(id="output-table")
#                                                 ),
#                                             ],
#                                             className="shadow-sm",
#                                         ),
#                                         width=10,
#                                     ),
#                                 ],
#                                 className="justify-content-center mb-4",
#                             ),
#                             dbc.Row(
#                                 [
#                                     dbc.Col(
#                                         dbc.Card(
#                                             [
#                                                 dbc.CardHeader(
#                                                     "Dataset Summary (Data Types & Missing Values)",
#                                                     className="bg-dark text-white",
#                                                 ),
#                                                 dbc.CardBody(
#                                                     html.Div(id="data-summary")
#                                                 ),
#                                             ],
#                                             className="shadow-sm",
#                                         ),
#                                         width=10,
#                                     ),
#                                 ],
#                                 className="justify-content-center mb-4",
#                             ),
#                         ],
#                     ),
#                     # Statistics Tab
#                     dbc.Tab(
#                         label="📊 Statistics",
#                         tab_id="tab-statistics",
#                         children=[
#                             dbc.Row(
#                                 [
#                                     dbc.Col(
#                                         dbc.Card(
#                                             [
#                                                 dbc.CardHeader(
#                                                     "Statistical Summary",
#                                                     className="bg-secondary text-white",
#                                                 ),
#                                                 dbc.CardBody(
#                                                     html.Div(id="stats-table")
#                                                 ),
#                                             ],
#                                             className="shadow-sm",
#                                         ),
#                                         width=10,
#                                     ),
#                                 ],
#                                 className="justify-content-center mb-4",
#                             ),
#                         ],
#                     ),
#                     # Visualizations Tab
#                     dbc.Tab(
#                         label="📈 Visualizations",
#                         tab_id="tab-visuals",
#                         children=[
#                             dbc.Row(
#                                 [
#                                     dbc.Col(
#                                         dbc.Card(
#                                             [
#                                                 dbc.CardHeader(
#                                                     "Feature Analysis",
#                                                     className="bg-info text-white",
#                                                 ),
#                                                 dbc.CardBody(
#                                                     [
#                                                         # Styled Dropdown
#                                                         html.Div(
#                                                             dcc.Dropdown(
#                                                                 id="column-dropdown",
#                                                                 placeholder="Select a feature for analysis...",
#                                                                 className="dropdown-style",
#                                                             ),
#                                                             className="mb-4",
#                                                         ),
#                                                         # Grouped Cards for Visualizations
#                                                         dbc.Row(
#                                                             [
#                                                                 # Feature Distribution
#                                                                 dbc.Col(
#                                                                     dbc.Card(
#                                                                         [
#                                                                             dbc.CardHeader(
#                                                                                 "Feature Distribution"
#                                                                             ),
#                                                                             dbc.CardBody(
#                                                                                 dcc.Graph(
#                                                                                     id="distribution-plot"
#                                                                                 )
#                                                                             ),
#                                                                         ],
#                                                                         className="shadow-sm",
#                                                                     ),
#                                                                     width=6,
#                                                                 ),
#                                                                 # Outlier Detection
#                                                                 dbc.Col(
#                                                                     dbc.Card(
#                                                                         [
#                                                                             dbc.CardHeader(
#                                                                                 "Outlier Detection"
#                                                                             ),
#                                                                             dbc.CardBody(
#                                                                                 [
#                                                                                     # Dropdown to select outlier detection algorithm
#                                                                                     dcc.Dropdown(
#                                                                                         id="outlier-algo-dropdown",
#                                                                                         options=[
#                                                                                             {
#                                                                                                 "label": "Z-Score",
#                                                                                                 "value": "zscore",
#                                                                                             },
#                                                                                             {
#                                                                                                 "label": "IQR",
#                                                                                                 "value": "iqr",
#                                                                                             },
#                                                                                             {
#                                                                                                 "label": "DBSCAN",
#                                                                                                 "value": "dbscan",
#                                                                                             },
#                                                                                             {
#                                                                                                 "label": "Isolation Forest",
#                                                                                                 "value": "isolation_forest",
#                                                                                             },
#                                                                                         ],
#                                                                                         value="zscore",  # Default algorithm
#                                                                                         placeholder="Select an outlier detection algorithm...",
#                                                                                         className="dropdown-style mb-3",
#                                                                                     ),
#                                                                                     dcc.Graph(
#                                                                                         id="outlier-boxplot"
#                                                                                     ),
#                                                                                 ]
#                                                                             ),
#                                                                         ],
#                                                                         className="shadow-sm",
#                                                                     ),
#                                                                     width=6,
#                                                                 ),
#                                                             ],
#                                                             className="mb-4",
#                                                         ),
#                                                         # Correlation Heatmap
#                                                         dbc.Row(
#                                                             [
#                                                                 dbc.Col(
#                                                                     dbc.Card(
#                                                                         [
#                                                                             dbc.CardHeader(
#                                                                                 "Feature Correlation Heatmap"
#                                                                             ),
#                                                                             dbc.CardBody(
#                                                                                 [
#                                                                                     # Dropdown to toggle correlation algorithms
#                                                                                     dcc.Dropdown(
#                                                                                         id="correlation-method-dropdown",
#                                                                                         options=[
#                                                                                             {
#                                                                                                 "label": "Pearson (default)",
#                                                                                                 "value": "pearson",
#                                                                                             },
#                                                                                             {
#                                                                                                 "label": "Spearman",
#                                                                                                 "value": "spearman",
#                                                                                             },
#                                                                                             {
#                                                                                                 "label": "Kendall",
#                                                                                                 "value": "kendall",
#                                                                                             },
#                                                                                         ],
#                                                                                         value="pearson",  # Default to Pearson
#                                                                                         placeholder="Select correlation method...",
#                                                                                         className="dropdown-style mb-3",
#                                                                                     ),
#                                                                                     dcc.Graph(
#                                                                                         id="correlation-heatmap"
#                                                                                     ),
#                                                                                 ]
#                                                                             ),
#                                                                         ],
#                                                                         className="shadow-sm",
#                                                                     ),
#                                                                     width=12,
#                                                                 ),
#                                                             ]
#                                                         ),
#                                                     ],
#                                                 ),
#                                             ],
#                                             className="shadow-sm",
#                                         ),
#                                         width=12,
#                                     ),
#                                 ],
#                                 className="justify-content-center mb-4",
#                             ),
#                         ],
#                     ),
#                     # Machine Learning Insights Tab
#                     dbc.Tab(
#                         label="🤖 Feature Importance",
#                         tab_id="tab-feature-importance",
#                         children=[
#                             dbc.Row(
#                                 [
#                                     dbc.Col(
#                                         dbc.Card(
#                                             [
#                                                 dbc.CardHeader(
#                                                     "Feature Importance (ML Explainability)"
#                                                 ),
#                                                 dbc.CardBody(
#                                                     [
#                                                         dcc.Dropdown(
#                                                             id="target-column",
#                                                             placeholder="Select target column...",
#                                                             className="dropdown-style",
#                                                         ),
#                                                         dcc.Graph(
#                                                             id="feature-importance-plot"
#                                                         ),
#                                                     ]
#                                                 ),
#                                             ],
#                                             className="shadow-sm",
#                                         ),
#                                         width=10,
#                                     ),
#                                 ],
#                                 className="justify-content-center",
#                             ),
#                         ],
#                     ),
#                 ],
#                 id="eda-tabs",
#                 active_tab="tab-overview",
#             ),
#         ],
#         fluid=True,
#         className="p-4",
#     )
