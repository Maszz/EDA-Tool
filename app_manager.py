import dash
import dash_bootstrap_components as dbc
from dash import Dash, html
from flask import request

from callbacks.feature_importances import (
    register_feature_importance_plot_callbacks,
    register_feature_importance_selector_callbacks,
)
from callbacks.file_callbacks import register_file_callbacks
from callbacks.overviews import (
    register_data_summary_callbacks,
    register_duplicate_rows_callbacks,
    register_file_summary_callbacks,
    register_head_table_callbacks,
)
from callbacks.statistics import (
    register_correlation_heatmap_callbacks,
    register_feature_distribution_callbacks,
    register_outlier_detection_callbacks,
    register_statistic_table_callbacks,
    register_statistics_selector_callbacks,
)
from callbacks.visualizations import (
    register_bar_plot_callbacks,
    register_pair_plot_callbacks,
    register_parallel_coordinates_callbacks,
    register_contour_plot_callbacks,
    register_scatter_plot_callbacks,
    register_violin_plot_callbacks,
    register_visualization_selector_callbacks,
)
from callbacks.data_cleaning import (
    register_data_cleaning_callbacks,
    register_data_cleaning_selector_callbacks,
)
from components.upload import upload_component
from utils.logger_config import logger  # Import the logger
from utils.store import Store


class AppManager:
    def __init__(self):
        # Initialize the Dash app
        self.initialize_store()
        self.create_app()

        self.app_config()

        # Register callbacks
        self.register_callbacks()

    def create_app(self) -> "Dash":
        self.app = Dash(
            "App Name", use_pages=True, external_stylesheets=[dbc.themes.BOOTSTRAP]
        )

        # Log every incoming request
        @self.app.server.before_request
        def log_request() -> None:
            logger.info(
                f"📥 Incoming Request: {request.method} {request.path} from {request.remote_addr}"
            )
            self.app.layout = self.create_layout()

    def create_layout(self) -> "html.Div":
        """Define the layout with a modern sticky top navigation bar and embedded CSS."""
        return html.Div(
            style={
                "minHeight": "100vh",
                "display": "flex",
                "flexDirection": "column",
                "backgroundColor": "#f8f9fa",
            },
            children=[
                # Sticky Top Navbar with CSS Styling
                dbc.Navbar(
                    [
                        dbc.Container(
                            style={
                                "display": "flex",
                                "justifyContent": "space-between",
                                "alignItems": "center",
                                "width": "100%",
                            },
                            children=[
                                # Logo / Brand Name
                                html.Div(
                                    "📊 EDA Tool",
                                    style={
                                        "fontSize": "24px",
                                        "fontWeight": "bold",
                                        "color": "white",
                                        "cursor": "pointer",
                                    },
                                ),
                                # Navigation Links
                                dbc.Nav(
                                    [
                                        dbc.NavLink(
                                            "📋 Data Overview",
                                            href="/",
                                            active="exact",
                                            style={
                                                "color": "white",
                                                "padding": "12px 15px",
                                                "borderRadius": "5px",
                                                "textDecoration": "none",
                                                "transition": "0.3s",
                                            },
                                            className="nav-item",
                                        ),
                                        dbc.NavLink(
                                            "📊 Statistics",
                                            href="/statistics",
                                            active="exact",
                                            style={
                                                "color": "white",
                                                "padding": "12px 15px",
                                                "borderRadius": "5px",
                                                "textDecoration": "none",
                                                "transition": "0.3s",
                                            },
                                            className="nav-item",
                                        ),
                                        dbc.NavLink(
                                            "📈 Visualizations",
                                            href="/visualization",
                                            active="exact",
                                            style={
                                                "color": "white",
                                                "padding": "12px 15px",
                                                "borderRadius": "5px",
                                                "textDecoration": "none",
                                                "transition": "0.3s",
                                            },
                                            className="nav-item",
                                        ),
                                        dbc.NavLink(
                                            "🤖 Feature Importance",
                                            href="/feature-importance",
                                            active="exact",
                                            style={
                                                "color": "white",
                                                "padding": "12px 15px",
                                                "borderRadius": "5px",
                                                "textDecoration": "none",
                                                "transition": "0.3s",
                                            },
                                            className="nav-item",
                                        ),
                                        dbc.NavLink(
                                            "🧹 Data Cleaning",
                                            href="/data-cleaning",
                                            active="exact",
                                            style={
                                                "color": "white",
                                                "padding": "12px 15px",
                                                "borderRadius": "5px",
                                                "textDecoration": "none",
                                                "transition": "0.3s",
                                            },
                                            className="nav-item",
                                        ),
                                    ],
                                    navbar=True,
                                    style={"display": "flex", "gap": "10px"},
                                ),
                            ],
                        )
                    ],
                    color="dark",
                    dark=True,
                    sticky="top",
                    style={
                        "padding": "10px",
                        "borderRadius": "0px",
                        "boxShadow": "0px 4px 8px rgba(0,0,0,0.2)",
                    },
                ),
                # Upload Section (Always Visible)
                dbc.Container(
                    style={
                        "padding": "20px",
                        "borderRadius": "10px",
                        "backgroundColor": "white",
                        "boxShadow": "0px 4px 8px rgba(0,0,0,0.1)",
                        "textAlign": "center",
                        "marginTop": "20px",
                    },
                    children=[
                        html.H1(
                            "📊 Exploratory Data Analysis Tool",
                            className="display-4",
                            style={"color": "#343a40", "fontWeight": "bold"},
                        ),
                        html.P(
                            "A simple yet powerful tool to explore your datasets.",
                            className="lead",
                            style={"color": "#6c757d"},
                        ),
                        dbc.Row(
                            [
                                dbc.Col(
                                    upload_component(), width=4
                                ),  # AI Summary Box (Right)
                                # dbc.Col(
                                #     dbc.Card(
                                #         [
                                #             dbc.CardHeader(
                                #                 "🧠 AI Summary",
                                #                 className="bg-info text-white",
                                #             ),
                                #             dbc.CardBody(
                                #                 dcc.Markdown(
                                #                     id="ai-summary",
                                #                     style={
                                #                         "height": "250px",
                                #                         "overflowY": "auto",
                                #                         "border": "1px solid #ddd",
                                #                         "borderRadius": "5px",
                                #                         "padding": "10px",
                                #                         "backgroundColor": "#f8f9fa",
                                #                         "fontSize": "14px",
                                #                     },
                                #                 ),
                                #             ),
                                #         ],
                                #         className="shadow-sm",
                                #         style={"height": "100%"},
                                #     ),
                                #     width=8,
                                # ),
                            ],
                            className="justify-content-center my-3",
                        ),
                    ],
                    fluid=True,
                ),
                # Page Content (Dynamic)
                html.Div(
                    dash.page_container,
                    style={
                        "flex": "1",
                        "padding": "20px",
                        "borderRadius": "10px",
                        "backgroundColor": "white",
                        "boxShadow": "0px 4px 8px rgba(0,0,0,0.1)",
                        "margin": "20px",
                        "minHeight": "500px",
                    },
                ),
                # Footer
                html.Footer(
                    html.Div(
                        "© 2025 Exploratory Data Analysis Tool",
                        className="text-center text-muted py-3",
                        style={
                            "marginTop": "auto",
                            "padding": "10px",
                            "backgroundColor": "white",
                            "borderRadius": "10px",
                            "boxShadow": "0px 4px 8px rgba(0,0,0,0.1)",
                            "textAlign": "center",
                        },
                    ),
                ),
            ],
        )

    def app_config(self) -> None:
        self.app.config["prevent_initial_callbacks"] = "initial_duplicate"
        self.app.config["suppress_callback_exceptions"] = True
        self.app.config["include_pages_meta"] = True
        self.app.config["title"] = "Dash"
        self.app.config["update_title"] = "Updating..."

    def register_callbacks(self) -> None:
        """Register all callbacks for the app."""
        register_file_callbacks(self.app)

        # Register Overview Callbacks
        register_head_table_callbacks(self.app)
        register_duplicate_rows_callbacks(self.app)
        register_file_summary_callbacks(self.app)
        register_data_summary_callbacks(self.app)

        # Register Statistics Callbacks
        register_statistic_table_callbacks(self.app)
        register_statistics_selector_callbacks(self.app)
        register_correlation_heatmap_callbacks(self.app)
        register_feature_distribution_callbacks(self.app)
        register_outlier_detection_callbacks(self.app)

        # Register Visualization Callbacks
        register_bar_plot_callbacks(self.app)
        register_pair_plot_callbacks(self.app)
        register_scatter_plot_callbacks(self.app)
        register_violin_plot_callbacks(self.app)
        register_visualization_selector_callbacks(self.app)
        register_parallel_coordinates_callbacks(self.app)
        register_contour_plot_callbacks(self.app)

        # Register Feature Importance Callbacks
        register_feature_importance_selector_callbacks(self.app)
        register_feature_importance_plot_callbacks(self.app)

        # Register Data Cleaning Callbacks
        register_data_cleaning_callbacks(self.app)
        register_data_cleaning_selector_callbacks(self.app)
        # register_head_table_callbacks(self.app)
        # register_stat_table_callbacks(self.app)
        # register_missing_values_callbacks(self.app)
        # register_feature_distribution_callbacks(self.app)
        # register_outlier_detection_callbacks(self.app)
        # register_correlation_heatmap_callbacks(self.app)
        # register_feature_importance_callbacks(self.app)
        # register_missing_values_heatmap_callbacks(self.app)
        # register_visualization_callbacks(self.app)

    def initialize_store(self) -> None:
        self.store = Store()
        self.store.register("data_frame", None)
        self.store.register("filename", None)
