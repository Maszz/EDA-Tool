import dash
from dash import Dash, html

from callbacks.file_callbacks import register_file_callbacks
from callbacks.head_table_callback import register_head_table_callbacks
from callbacks.statistic_table_callback import register_stat_table_callbacks
from callbacks.data_summary_callback import register_missing_values_callbacks
from callbacks.feature_distribution_callbacks import (
    register_feature_distribution_callbacks,
)
from callbacks.outlier_detection_callbacks import register_outlier_detection_callbacks
from callbacks.correlation_heatmap_callbacks import (
    register_correlation_heatmap_callbacks,
)
from callbacks.feature_importance_callbacks import register_feature_importance_callbacks
from utils.store import Store
import dash_bootstrap_components as dbc


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
        self.app.layout = self.create_layout()

    def create_layout(self) -> "html.Div":
        """Define the layout of the app."""
        # return html.Div(
        #     [
        #         html.H1("Scalable Dash App"),
        #         upload_component(),
        #         html.Button("Reset", id="reset-button", n_clicks=0),
        #         html.Div(id="output-table"),
        #     ]
        # )
        return html.Div(
            [
                dash.page_container,
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
        register_head_table_callbacks(self.app)
        register_stat_table_callbacks(self.app)
        register_missing_values_callbacks(self.app)
        register_feature_distribution_callbacks(self.app)
        register_outlier_detection_callbacks(self.app)
        register_correlation_heatmap_callbacks(self.app)
        register_feature_importance_callbacks(self.app)

    def initialize_store(self) -> None:
        self.store = Store()
        self.store.register("data_frame", None)
