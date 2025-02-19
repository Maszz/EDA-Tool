import argparse
import json
import pickle
import pprint
from pathlib import Path
import joblib

CACHE_DIR = Path("./.cache")  # Default cache directory


def load_pickle_file(file_path: Path):
    """Loads a pickle file and returns its content."""
    try:
        return joblib.load(file_path)
    except (EOFError, pickle.UnpicklingError) as e:
        print(f"⚠️ Skipping corrupted file {file_path}: {e}")
        return None
    except Exception as e:
        print(f"❌ Failed to load {file_path}: {e}")
        return None


def beautify_cache_data(data):
    """Formats data in a human-readable way."""
    try:
        return json.dumps(data, indent=6, ensure_ascii=True)
    except (TypeError, ValueError):
        return pprint.pformat(data, indent=4, width=120)


def get_cache_files_by_hash(cache_hash: str):
    """Finds the index and all data files for a given hash."""
    index_file = CACHE_DIR / f"{cache_hash}_index.pkl"

    if not index_file.exists():
        print(f"❌ No cache found for hash: {cache_hash}")
        return None, []

    # Find all corresponding data files
    data_files = sorted(CACHE_DIR.glob(f"{cache_hash}_data*.pkl"))

    return index_file, data_files


def dump_cache_by_hash(
    cache_hash: str | None, output_path: str | None = None, pretty: bool | None = None
) -> None:
    """Dumps cache data for a given hash."""
    if not cache_hash:
        print("❌ Please specify a hash using --cache-hash")
        return

    index_file, data_files = get_cache_files_by_hash(cache_hash)

    if not index_file or not data_files:
        return

    print(f"\n📂 **Inspecting cache:** {index_file.name}")

    index_data = load_pickle_file(index_file)
    if not index_data:
        print("❌ Failed to load index data.")
        return

    print("\n📌 **Index Data:**")
    formatted_index = beautify_cache_data(index_data)
    print(formatted_index)

    results = {"index": formatted_index, "data": {}}

    # Read all data parts
    for data_file in data_files:
        print(f"\n📂 **Inspecting data file:** {data_file.name}")
        data_cache = load_pickle_file(data_file)
        if pretty:
            formatted_data = beautify_cache_data(data_cache)
        else:
            formatted_data = data_cache

        print("\n📌 **Cached Data:**")
        print(formatted_data)

        results["data"][data_file.name] = formatted_data

    # Save to file if requested
    if output_path:
        output_file = Path(output_path)
        with output_file.open("w", encoding="utf-8") as f:
            json.dump(results, f, indent=4, ensure_ascii=False)
        print(f"\n✅ Cache dump saved to {output_file}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Inspect and dump cache files by hash."
    )
    parser.add_argument(
        "--cache-hash", type=str, help="Specify a cache hash to inspect."
    )
    parser.add_argument(
        "--output", type=str, help="Optional file to save the formatted dump."
    )
    parser.add_argument(
        "--pretty",
        type=bool,
        help="Pretty print the cache data.",
        default=False,
    )

    args = parser.parse_args()
    dump_cache_by_hash(
        cache_hash=args.cache_hash, output_path=args.output, pretty=args.pretty
    )
