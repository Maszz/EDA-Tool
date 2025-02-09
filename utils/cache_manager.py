import hashlib
import os
import pickle
from pathlib import Path
from typing import Any

import polars as pl

from utils.logger_config import logger  # Import logger


class CacheManager:
    """Handles in-memory and file-based caching with file chunking for large datasets."""

    CACHE_DIR = Path("./.cache")  # Persistent cache directory
    MEMORY_CACHE: dict[str, Any] = {}  # In-memory cache
    MAX_FILE_SIZE = 100 * 1024 * 1024  # 100MB per cache file
    ENABLE_CACHE = os.environ.get("ENABLE_CACHE", "true").lower() == "true"

    def __init__(self):
        """Initialize cache manager and ensure cache directory exists."""
        self.CACHE_DIR.mkdir(exist_ok=True)
        logger.info(f"✅ CacheManager initialized. Cache Enabled: {self.ENABLE_CACHE}")

    @staticmethod
    def compute_file_hash(df: pl.DataFrame) -> str:
        """Generates a unique hash for a DataFrame to detect changes."""
        df_copy = df.clone()
        df_bytes = df_copy.write_csv().encode("utf-8")
        return hashlib.md5(df_bytes).hexdigest()

    def get_cache_index_file(self, df: pl.DataFrame) -> Path:
        """Returns the index file path based on the dataset hash."""
        file_hash = self.compute_file_hash(df)
        return self.CACHE_DIR / f"{file_hash}_index.pkl"

    def get_cache_data_file(self, df: pl.DataFrame, part_number: int) -> Path:
        """Returns the cache data file path based on dataset hash and part number."""
        file_hash = self.compute_file_hash(df)
        return self.CACHE_DIR / f"{file_hash}_data{part_number}.pkl"

    def load_cache(self, cache_key: str, df: pl.DataFrame) -> Any:
        """Loads cached results from memory or disk if available."""
        if not self.ENABLE_CACHE:
            logger.info(f"🔧 Cache disabled. Skipping load for {cache_key}.")
            return None

        index_file = self.get_cache_index_file(df)

        # ✅ Load index file if exists
        if index_file.exists():
            try:
                with index_file.open("rb") as f:
                    index_data = pickle.load(f)
            except Exception as e:
                logger.error(f"❌ Failed to read index file: {e}")
                return None
        else:
            return None  # No index means no cache

        # ✅ Check if the cache key exists in any part file
        if cache_key in index_data:
            part_number = index_data[cache_key]
            data_file = self.get_cache_data_file(df, part_number)

            # ✅ Load the cached data from file
            if data_file.exists():
                try:
                    with data_file.open("rb") as f:
                        file_cache = pickle.load(f)
                        if cache_key in file_cache:
                            logger.info(
                                f"✅ Cache hit for {cache_key} (Part {part_number})"
                            )
                            return file_cache[cache_key]
                except Exception as e:
                    logger.error(f"❌ Cache file corrupted: {e}")

        return None  # Cache miss

    def save_cache(self, cache_key: str, df: pl.DataFrame, data: Any) -> None:
        """Stores computed results in memory and file cache with file size management."""
        if not self.ENABLE_CACHE:
            logger.info(f"🔧 Cache disabled. Skipping save for {cache_key}.")
            return

        index_file = self.get_cache_index_file(df)
        index_data = {}

        # ✅ Load index file if it exists
        if index_file.exists():
            try:
                with index_file.open("rb") as f:
                    index_data = pickle.load(f)
            except Exception as e:
                logger.error(f"❌ Failed to read index file: {e}")
                index_data = {}

        # ✅ Remove old cache entry if it exists
        if cache_key in index_data:
            old_part_number = index_data[cache_key]
            old_data_file = self.get_cache_data_file(df, old_part_number)

            if old_data_file.exists():
                try:
                    with old_data_file.open("rb") as f:
                        old_cache = pickle.load(f)

                    # Remove the old key from the cache
                    if cache_key in old_cache:
                        del old_cache[cache_key]

                    # Save back the cleaned file
                    with old_data_file.open("wb") as f:
                        pickle.dump(old_cache, f)

                    logger.info(
                        f"🗑️ Removed old cache entry for {cache_key} from Part {old_part_number}"
                    )

                except Exception as e:
                    logger.error(f"❌ Error removing old cache entry: {e}")

        # ✅ Find the latest part number
        part_number = max(index_data.values(), default=1)
        data_file = self.get_cache_data_file(df, part_number)

        # ✅ Load or create cache part file
        if data_file.exists():
            try:
                with data_file.open("rb") as f:
                    file_cache = pickle.load(f)
            except Exception as e:
                logger.error(f"❌ Failed to read existing cache file: {e}")
                file_cache = {}
        else:
            file_cache = {}

        # ✅ Check if removing the old key made enough space
        estimated_size = pickle.dumps({cache_key: data})
        if (
            len(estimated_size)
            + (data_file.stat().st_size if data_file.exists() else 0)
            > self.MAX_FILE_SIZE
        ):
            # Move to a new part
            part_number += 1
            data_file = self.get_cache_data_file(df, part_number)
            file_cache = {}

        # ✅ Store in Memory and File
        file_cache[cache_key] = data
        self.MEMORY_CACHE[data_file] = file_cache  # Store in-memory for quick access

        # ✅ Save the data
        with data_file.open("wb") as f:
            pickle.dump(file_cache, f)

        # ✅ Update the index
        index_data[cache_key] = part_number
        self.MEMORY_CACHE[index_file] = index_data  # Store index in-memory

        with index_file.open("wb") as f:
            pickle.dump(index_data, f)

        logger.info(f"💾 Cache stored for {cache_key} in Part {part_number}")

    def clear_cache(self) -> None:
        """Clears all cached data from memory and disk."""
        if not self.ENABLE_CACHE:
            logger.info("🔧 Cache disabled. Skipping clear operation.")
            return

        self.MEMORY_CACHE.clear()
        for file in self.CACHE_DIR.glob("*.pkl"):
            try:
                file.unlink()
            except Exception as e:
                logger.error(f"❌ Failed to delete cache {file.name}: {e}")
        logger.info("🗑️ Cache cleared!")


# ✅ Singleton instance
CACHE_MANAGER = CacheManager()
