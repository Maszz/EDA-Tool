import dash
from dash import Dash, html

from callbacks.file_callbacks import register_file_callbacks
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
        self.app = Dash("App Name", use_pages=True)
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

    def initialize_store(self) -> None:
        self.store = Store()
        self.store.register("data_frame", None)
