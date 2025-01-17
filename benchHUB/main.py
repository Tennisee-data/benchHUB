#main.py
import json
import os
from datetime import datetime
import streamlit as st
from tabulate import tabulate
import pandas as pd
from benchHUB.config import config
from benchHUB.config.system_info import get_system_info
from benchHUB.cpu_bench import cpu_benchmark
from benchHUB.memory_bench import memory_benchmark
from benchHUB.gpu_bench import gpu_benchmark
from benchHUB.disk_bench import disk_benchmark
from benchHUB.ml_bench import ml_benchmark
from benchHUB.plot_bench import plot_benchmark
from benchHUB.db import BenchmarkDB
from benchHUB.utils.anonymise import anonymise_results
from benchHUB.utils.print_config import print_configuration

def validate_configuration():
    """
    Validate configuration variables from config.py.
    """
    for var_name, value in vars(config).items():
        if not var_name.startswith("__"):
            # Example validation
            if "SIZE" in var_name and not isinstance(value, int):
                raise ValueError(f"{var_name} must be an integer, got {type(value).__name__}.")
            if "SHAPE" in var_name and not (isinstance(value, tuple) and len(value) == 2):
                raise ValueError(f"{var_name} must be a tuple of length 2, got {value}.")

    print("bencHUB configuration validated successfully.")

def run_all_benchmarks(
    n_runs: int = config.N_RUNS_DEFAULT,
    disk_file_size: int = config.DISK_FILE_SIZE_DEFAULT,
    cpu_array_size: int = config.CPU_ARRAY_SIZE_DEFAULT,
    memory_shape: tuple = config.MEMORY_SHAPE_DEFAULT,
    gpu_matrix_shape: tuple = config.GPU_MATRIX_SHAPE_DEFAULT,
    animation_frames: int = config.ANIMATION_FRAMES,
    image_shape: tuple = config.IMAGE_SHAPE,
    plot_points: int = config.PLOT_POINTS_DEFAULT
):
    """
    Orchestrate all benchmarks with user-defined or default settings.
    """
    print("Gathering system info...")
    system_info = get_system_info()

    print("Running CPU benchmark...")
    cpu_results = cpu_benchmark(n_runs, cpu_array_size)

    print("Running Memory benchmark...")
    memory_results = memory_benchmark(n_runs, memory_shape)

    print("Running GPU benchmark...")
    gpu_results = gpu_benchmark(n_runs, gpu_matrix_shape)

    print("Running Disk benchmark...")
    disk_results = disk_benchmark(n_runs, disk_file_size)

    print("Running Machine Learning benchmark...")
    ml_results = ml_benchmark()

    print("Running Plotting benchmark...")
    plot_results = plot_benchmark(n_runs, plot_points)

    results = {
        'system_info': system_info,
        'cpu': cpu_results,
        'memory': memory_results,
        'gpu': gpu_results,
        'disk': disk_results,
        'ml': ml_results,
        'plot': plot_results
    }
    return results

def run_and_store():
    # 1. Run all benchmarks and get the results
    results = run_all_benchmarks()

    # 2. Create a DB instance (defaults to 'benchmark_results.db' file)
    db = BenchmarkDB()

    # 3. Store results in DB, with an optional note
    record_id = db.store_results(results, notes="Ran benchmarks on my local machine")
    print(f"Stored results under record_id: {record_id}")

    # 4. (Optional) Fetch them back and print
    all_results = db.fetch_results()
    print(f"Fetched {len(all_results)} results from DB.")

# Directory to store results
RESULTS_DIR = "results"

def save_results(results, results_dir=RESULTS_DIR, share_public=False):
    """
    Save benchmark results locally and optionally share publicly.
    
    Args:
        results (dict): benchHUB results.
        results_dir (str): Path to the directory where results will be saved.
        share_public (bool): Whether to save anonymized results publicly.
    """
    # Ensure results directory exists
    os.makedirs(results_dir, exist_ok=True)

    # Generate a unique filename based on timestamp
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    local_filename = os.path.join(results_dir, f"benchmark_{timestamp}.json")
    
    # Save locally
    with open(local_filename, "w") as f:
        json.dump(results, f, indent=4)
    print(f"Results saved locally at: {local_filename}")

    # Optionally share publicly
    if share_public:
        anonymised_results = anonymise_results(results)
        public_filename = os.path.join(results_dir, f"public_benchmark_{timestamp}.json")
        with open(public_filename, "w") as f:
            json.dump(anonymised_results, f, indent=4)
        print(f"Anonymised results saved publicly at: {public_filename}")

def show_results_in_table():
    db = BenchmarkDB() 
    rows = db.fetch_results()
    # Convert them to a DataFrame
    df = pd.DataFrame(rows)
    # For JSON fields, either keep them as-is or flatten them
    # e.g. df['cpu_floating_point'] = df['cpu'].apply(lambda x: x.get('floating_point', None))

    # Print table in the console with sorting by 'timestamp'
    df.sort_values('timestamp', inplace=True)
    print(tabulate(df, headers='keys', tablefmt='github'))  # or 'plain', 'fancy_grid', etc.

def show_results_web():
    db = BenchmarkDB()
    results = db.fetch_results()
    df = pd.DataFrame(results)

    # Flatten out some columns if you want. E.g.:
    # df['cpu_floating_point'] = df['cpu'].apply(lambda x: x.get('floating_point') if x else None)

    st.title("benchHUB Results")
    st.dataframe(df)  # Scrollable and users can sort columns

if __name__ == '__main__':
    validate_configuration()
    print_configuration()
    print("Running benchHUB benchmarks...")
    results = run_all_benchmarks()

    # Ask user for consent to share results publicly
    share = input("Do you want to share your results publicly? (yes/no): ").strip().lower() == "yes"

    # Save results locally and optionally publicly
    save_results(results, share_public=share)
