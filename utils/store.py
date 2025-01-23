import threading
from collections.abc import Callable
from typing import Any


class Store:
    """Thread-safe singleton state management class."""

    _instance = None
    _lock = threading.Lock()  # Class-level lock for singleton initialization

    def __new__(cls, *args: tuple[any], **kwargs: dict[str, Any]):
        """Ensure only one instance of Store is created."""
        if not cls._instance:
            cls._instance = super().__new__(cls, *args, **kwargs)
        return cls._instance

    def __init__(self):
        """Initialize the instance state only once."""
        if hasattr(self, "state"):
            return  # Prevent reinitialization
        self.state = {}
        self.state_lock = threading.Lock()

    # Internal helper for static methods to access the singleton instance
    @classmethod
    def _get_instance(cls) -> "Store":
        return cls()

    # Instance Methods
    def register(self, key: str, default: Any) -> None:
        """Register a new key in the store with a default value."""
        with self.state_lock:
            if key in self.state:
                raise ValueError(f"Key '{key}' is already registered.")
            self.state[key] = default

    def update(self, key: str, updater: Callable[[Any], Any]) -> None:
        """Update the value of a key using a lambda function."""
        with self.state_lock:
            if key not in self.state:
                raise KeyError(f"Key '{key}' is not registered in the store.")
            self.state[key] = updater(self.state[key])

    def set(self, key: str, value: Any) -> None:
        """Set the value of a key directly."""
        with self.state_lock:
            if key not in self.state:
                raise KeyError(f"Key '{key}' is not registered in the store.")
            self.state[key] = value

    def get(self, key: str) -> Any:
        """Retrieve the value of a key."""
        with self.state_lock:
            if key not in self.state:
                raise KeyError(f"Key '{key}' is not registered in the store.")
            return self.state[key]

    def get_all(self) -> dict:
        """Retrieve a copy of the entire state."""
        with self.state_lock:
            return self.state.copy()

    def reset(self) -> None:
        """Reset the store to an empty state."""
        with self.state_lock:
            self.state.clear()

    # Static Methods for Global Access
    @staticmethod
    def register_static(key: str, default: Any) -> None:
        """Static method to register a new key in the store."""
        Store._get_instance().register(key, default)

    @staticmethod
    def update_static(key: str, updater: Callable[[Any], Any]) -> None:
        """Static method to update the value of a key."""
        Store._get_instance().update(key, updater)

    @staticmethod
    def set_static(key: str, value: Any) -> None:
        """Static method to set the value of a key."""
        Store._get_instance().set(key, value)

    @staticmethod
    def get_static(key: str) -> Any:
        """Static method to retrieve the value of a key."""
        return Store._get_instance().get(key)

    @staticmethod
    def get_all_static() -> dict:
        """Static method to retrieve the entire state."""
        return Store._get_instance().get_all()

    @staticmethod
    def reset_static() -> None:
        """Static method to reset the store."""
        Store._get_instance().reset()
