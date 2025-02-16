import time
import random
import sys
import os
import csv
import gc
from statistics import mean, stdev

# Import Python dict-based HashTable
sys.path.insert(0, os.getcwd())
from native_hashtable import HashTable  # ✅ Ensure this is correctly implemented

# Import Cython HashTable
from src import CHashTable  # ✅ Import your compiled Cython module

# Number of operations for benchmarking
NUM_ITEMS = 10_000_000
NUM_RUNS = 10  # ✅ Run multiple rounds and compute averages

# Generate random keys and values
keys = [f"key{i}" for i in range(NUM_ITEMS)]
values = [random.randint(0, 10000) for _ in range(NUM_ITEMS)]


def benchmark_hash_table(table_class, label):
    """Benchmark a hash table implementation."""
    times = {"insert": [], "lookup": [], "delete": []}
    total_time = 0  # Track total execution time

    execution_times = []  # Store per-round execution times

    for run in range(NUM_RUNS):
        gc.collect()  # ✅ Reduce GC interference
        ht = table_class(size=8)

        start_run = time.perf_counter()

        # Insert
        start = time.perf_counter()
        for key, value in zip(keys, values):
            ht[key] = value
        insert_time = time.perf_counter() - start

        # Lookup
        start = time.perf_counter()
        for key in keys:
            assert ht[key] == values[int(key[3:])]
        lookup_time = time.perf_counter() - start

        # Delete
        start = time.perf_counter()
        for key in keys:
            del ht[key]
        delete_time = time.perf_counter() - start

        run_time = time.perf_counter() - start_run
        total_time += run_time

        # Store times
        times["insert"].append(insert_time)
        times["lookup"].append(lookup_time)
        times["delete"].append(delete_time)

        execution_times.append([run + 1, label, insert_time, lookup_time, delete_time])

    return times, total_time, execution_times


# Run benchmarks
implementations = [
    ("Python HashTable", HashTable),
    ("Cython HashTable (Optimized)", CHashTable),
]
benchmark_results = {}
total_times = {}
total_op_times = {
    label: {"insert": 0, "lookup": 0, "delete": 0} for label, _ in implementations
}
execution_logs = {}

overall_total_time = 0


for label, impl in implementations:
    print(f"Benchmarking {label}...")
    times, total_time, exec_times = benchmark_hash_table(impl, label)
    benchmark_results[label] = times
    total_times[label] = total_time
    execution_logs[label] = exec_times
    overall_total_time += total_time

    # ✅ Store per-implementation operation times
    for op in ["insert", "lookup", "delete"]:
        total_op_times[label][op] = sum(times[op])

# Compute averages and standard deviation
results = {
    label: {op: (mean(times[op]), stdev(times[op])) for op in times}
    for label, times in benchmark_results.items()
}

# Print results
table_headers = ["Operation"] + list(results.keys())
print("\nResults (Time in seconds, avg ± std):")
print(f"{table_headers[0]:<15} {' '.join(f'{h:<25}' for h in table_headers[1:])}")
print("=" * 80)
for op in ["insert", "lookup", "delete"]:
    row = [f"{op.capitalize():<15}"]
    for label in results:
        avg, std = results[label][op]
        text = f"{avg:.6f} ± {std:.6f}"
        row.append(f"{text:25}")

    print(" ".join(row))

# Print total execution time summary
print("\nTotal Execution Time Summary:")
print(f"{'Implementation':<30} {'Total Execution Time (s)':<30}")
print("=" * 60)
for label, total_time in total_times.items():
    print(f"{label:<30} {total_time:.6f}")

# Print total operation execution times
print("\nTotal Operation Execution Time Summary:")
print(f"{'impl':<30} {'lookup':<15} {'insert':<15} {'delete':<15}")
print("=" * 80)
for impl, total_time in total_op_times.items():
    print(
        f"{impl:<30} {total_time['lookup']:<15.6f} {total_time['insert']:<15.6f} {total_time['delete']:<15.6f}"
    )


# Save execution logs to a CSV file
execution_log_csv = "execution_log.csv"
with open(execution_log_csv, "w", newline="") as csvfile:
    writer = csv.writer(csvfile)
    writer.writerow(
        [
            "Run",
            "Implementation",
            "Insert Time (s)",
            "Lookup Time (s)",
            "Delete Time (s)",
        ]
    )
    for label, exec_times in execution_logs.items():
        for row in exec_times:
            writer.writerow(row)

overall_total_time_csv = "overall_total_time.csv"
with open(overall_total_time_csv, "w", newline="") as csvfile:
    writer = csv.writer(csvfile)
    writer.writerow(["Implementation", "Total Execution Time (s)"])
    for label, total_time in total_times.items():
        writer.writerow([label, total_time])

total_op_times_csv = "total_op_times.csv"
with open(total_op_times_csv, "w", newline="") as csvfile:
    writer = csv.writer(csvfile)
    writer.writerow(["Implementation", "Operation", "Total Time (s)"])
    for label, op_times in total_op_times.items():
        for op, total_time in op_times.items():
            writer.writerow([label, op.capitalize(), total_time])

print(f"\n✅ Execution log saved to {execution_log_csv}!")
