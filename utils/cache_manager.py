# utils/cache_manager.py

import os
import json
import hashlib
import polars as pl
import pickle
from pathlib import Path
from typing import Any, Dict
from utils.logger_config import logger  # Import logger


class CacheManager:
    """Handles in-memory and file-based caching for expensive computations."""

    CACHE_DIR = Path("./.cache")  # Persistent cache directory
    MEMORY_CACHE: Dict[str, Any] = {}  # In-memory cache

    def __init__(self):
        """Initialize cache manager and ensure cache directory exists."""
        self.CACHE_DIR.mkdir(exist_ok=True)
        logger.info("✅ CacheManager initialized.")

    @staticmethod
    def compute_file_hash(df: pl.DataFrame) -> str:
        """Generates a unique hash for a DataFrame to detect changes."""
        df_copy = df.clone()  # Make sure it's a detached copy
        df_bytes = df_copy.write_csv().encode("utf-8")
        return hashlib.md5(df_bytes).hexdigest()

    def get_cache_file(self, df: pl.DataFrame) -> Path:
        """Returns the cache file path based on the dataset hash."""
        file_hash = self.compute_file_hash(df)
        return self.CACHE_DIR / f"{file_hash}.pkl"

    def load_cache(self, cache_key: str, df: pl.DataFrame) -> Any:
        """Loads cached results from memory or disk if available."""
        file_path = self.get_cache_file(df)

        # ✅ Check Memory Cache First
        if file_path in self.MEMORY_CACHE:
            if cache_key in self.MEMORY_CACHE[file_path]:
                logger.info(f"✅ Cache hit (Memory) for {cache_key}")
                return self.MEMORY_CACHE[file_path][cache_key]

        # ✅ Check File Cache
        if file_path.exists():
            try:
                with file_path.open("rb") as f:
                    file_cache = pickle.load(f)
                    self.MEMORY_CACHE[file_path] = file_cache  # Store in memory

                if cache_key in file_cache:
                    logger.info(f"✅ Cache hit (File) for {cache_key}")
                    return file_cache[cache_key]
            except Exception as e:
                logger.error(f"❌ Cache file corrupted: {e}")

        return None  # Cache miss

    def save_cache(self, cache_key: str, df: pl.DataFrame, data: Any):
        """Stores computed results in memory and file cache."""
        file_path = self.get_cache_file(df)

        # ✅ Load existing file cache or create a new one
        if file_path.exists():
            try:
                with file_path.open("rb") as f:
                    file_cache = pickle.load(f)
            except Exception as e:
                logger.error(f"❌ Failed to read existing cache: {e}")
                file_cache = {}
        else:
            file_cache = {}

        # ✅ Update Cache (Memory + File)
        file_cache[cache_key] = data
        self.MEMORY_CACHE[file_path] = file_cache  # Store in-memory for quick access

        with file_path.open("wb") as f:
            pickle.dump(file_cache, f)
        logger.info(f"💾 Cache stored for {cache_key}")

    def clear_cache(self):
        """Clears all cached data from memory and disk."""
        self.MEMORY_CACHE.clear()
        for file in self.CACHE_DIR.glob("*.pkl"):
            try:
                file.unlink()
            except Exception as e:
                logger.error(f"❌ Failed to delete cache {file.name}: {e}")
        logger.info("🗑️ Cache cleared!")


# ✅ Singleton instance
CACHE_MANAGER = CacheManager()
