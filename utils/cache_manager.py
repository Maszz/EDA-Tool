import hashlib
import os
from pathlib import Path
from typing import Any
import xxhash
import polars as pl

from utils.logger_config import logger  # Import logger

import joblib
import io
import threading


class CacheManager:
    """Handles in-memory and file-based caching with file chunking for large datasets."""

    CACHE_DIR = Path("./.cache")  # Persistent cache directory
    MEMORY_CACHE: dict[str, Any] = {}  # In-memory cache
    # MAX_FILE_SIZE = 100 * 1024 * 1024  # 100MB per cache file
    MAX_FILE_SIZE = 8 * 1024

    ENABLE_CACHE = os.environ.get("ENABLE_CACHE", "false").lower() == "true"
    ENABLE_SAMPLE = os.environ.get("ENABLE_SAMPLE", "false").lower() == "true"

    def __init__(self):
        """Initialize cache manager and ensure cache directory exists."""
        self.CACHE_DIR.mkdir(exist_ok=True)
        logger.info(f"✅ CacheManager initialized. Cache Enabled: {self.ENABLE_CACHE}")
        self.lock = threading.Lock()

    @staticmethod
    def compute_file_hash(df: pl.DataFrame, sample_size: int = 100) -> str:
        """Generates a fast hash for a DataFrame using sampling and xxHash."""
        df_clone = df.clone()
        if df_clone.is_empty():
            return xxhash.xxh64().hexdigest()  # Empty DataFrame hash

        hasher = xxhash.xxh64()
        if not CACHE_MANAGER.ENABLE_SAMPLE:
            df_sample = df_clone.clone()
        else:
            # Sample rows: Get first, middle, and last parts (or full DataFrame if small)
            num_rows = df.height
            if num_rows <= sample_size * 3:
                df_sample = df_clone.clone()
            else:
                df_sample = pl.concat(
                    [
                        df_clone.head(sample_size),
                        df_clone.slice(num_rows // 2, sample_size),
                        df_clone.tail(sample_size),
                    ]
                )

        # Sample columns: Hash only a subset of columns (if many exist)
        # num_cols = df_sample.width
        # selected_cols = df_sample.columns[
        #     : min(10, num_cols)
        # ]  # Use first 10 cols (or all if less)
        # df_sample = df_sample.select(selected_cols)

        # Convert DataFrame to bytes and hash it
        df_bytes = df_sample.write_csv().encode("utf-8")
        hasher.update(df_bytes)

        return hasher.hexdigest()

    def get_cache_index_file(self, df: pl.DataFrame) -> Path:
        """Returns the index file path based on the dataset hash."""
        file_hash = self.compute_file_hash(df)
        return self.CACHE_DIR / f"{file_hash}_index.pkl"

    def get_cache_data_file(self, df: pl.DataFrame, part_number: int) -> Path:
        """Returns the cache data file path based on dataset hash and part number."""
        file_hash = self.compute_file_hash(df)
        return self.CACHE_DIR / f"{file_hash}_data_{part_number}.pkl"

    def load_cache(self, cache_key: str, df: pl.DataFrame) -> Any:
        """Loads cached results from memory or disk if available."""
        if not self.ENABLE_CACHE:
            logger.info(f"🔧 Cache disabled. Skipping load for {cache_key}.")
            return None

        index_file = self.get_cache_index_file(df)

        # ✅ Load index file if exists
        if index_file.exists():
            try:

                index_data = self.load_from_file(index_file)
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
                    file_cache = self.load_from_file(data_file)
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
        with self.lock:
            index_file = self.get_cache_index_file(df)
            index_data = {}

            # ✅ Load index file if it exists
            if index_file.exists():
                try:
                    index_data = self.load_from_file(index_file)
                except Exception as e:
                    logger.error(f"❌ Failed to read index file: {e}")
                    index_data = {}

            # ✅ Remove old cache entry if it exists
            if cache_key in index_data:
                old_part_number = index_data[cache_key]
                old_data_file = self.get_cache_data_file(df, old_part_number)

                if old_data_file.exists():
                    try:
                        old_cache = self.load_from_file(old_data_file)

                        # Remove the old key from the cache
                        if cache_key in old_cache:
                            del old_cache[cache_key]

                        self.dump_to_file(old_data_file, old_cache)

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
                    # with data_file.open("rb") as f:
                    #     file_cache = pickle.load(f)
                    file_cache = self.load_from_file(data_file)
                except Exception as e:
                    logger.error(f"❌ Failed to read existing cache file: {e}")
                    file_cache = {}
            else:
                file_cache = {}

            # ✅ Check if removing the old key made enough space
            # estimated_size = pickle.dumps({cache_key: data})
            buffer = io.BytesIO()
            joblib.dump({cache_key: data}, buffer, compress=0)
            estimated_size = len(buffer.getvalue())

            available_part = None
            for part_number in sorted(
                set(index_data.values())
            ):  # Search existing parts
                data_file = self.get_cache_data_file(df, part_number)
                if not data_file.exists():
                    continue  # Skip non-existent files

                try:
                    file_cache = self.load_from_file(data_file)
                    current_size = data_file.stat().st_size

                    if current_size + estimated_size <= self.MAX_FILE_SIZE:
                        available_part = part_number
                        break  # ✅ Found a part that fits, stop searching
                except Exception as e:
                    logger.error(f"❌ Error reading cache part {part_number}: {e}")

            if available_part is None:
                available_part = max(
                    index_data.values(), default=1
                )  # Allocate next part
                data_file = self.get_cache_data_file(df, available_part)
                file_cache = {}  # Start a fresh cache

            else:
                data_file = self.get_cache_data_file(df, available_part)
                file_cache = (
                    self.load_from_file(data_file) if data_file.exists() else {}
                )

            # ✅ Store cache data

            # ✅ Store in Memory and File
            file_cache[cache_key] = data
            self.MEMORY_CACHE[data_file] = (
                file_cache  # Store in-memory for quick access
            )

            # ✅ Save the data
            self.dump_to_file(data_file, file_cache)

            # ✅ Update the index
            index_data[cache_key] = part_number
            self.MEMORY_CACHE[index_file] = index_data  # Store index in-memory

            self.dump_to_file(index_file, index_data)

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

    def load_from_file(self, path: str):
        return joblib.load(path)

    def dump_to_file(self, path: str, obj):
        return joblib.dump(obj, path, compress=0)


# ✅ Singleton instance
CACHE_MANAGER = CacheManager()
