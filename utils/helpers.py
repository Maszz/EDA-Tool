from .logger_config import logger
import plotly.graph_objects as go


def _log_and_return_empty(message: str):
    """Helper function to log a warning and return an empty figure."""
    logger.warning(message)
    return go.Figure(), message
