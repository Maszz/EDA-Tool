import plotly.graph_objects as go

from .logger_config import logger


def _log_and_return_empty(message: str):
    """Helper function to log a warning and return an empty figure."""
    logger.warning(message)
    return go.Figure(), message
