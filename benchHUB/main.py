import argparse
import json
import os
import sys
import uuid
from datetime import datetime
import multiprocessing
import threading
import time
import itertools

def spinning_cursor(stop_event):
    """A simple spinning cursor animation."""
    spinner = itertools.cycle(['-', '/', '|', '\\'])
    while not stop_event.is_set():
        sys.stdout.write(next(spinner))
        sys.stdout.flush()
        time.sleep(0.1)
        sys.stdout.write('\b')

def main():
    # --- Start Animation ---
    stop_animation_event = threading.Event()
    animation_thread = threading.Thread(target=spinning_cursor, args=(stop_animation_event,))
    print("🚀 Starting benchHUB, please wait while libraries are loading...")
    animation_thread.start()

    # --- Heavy Imports (run while animation is active) ---
    import requests
    from benchHUB.config import config
    from benchHUB.config.system_info import get_system_info
    from benchHUB.cpu_bench import cpu_benchmark
    from benchHUB.memory_bench import memory_benchmark
    from benchHUB.gpu_bench import gpu_benchmark
    from benchHUB.disk_bench import disk_benchmark
    from benchHUB.ml_bench import ml_benchmark
    from benchHUB.plot_bench import plot_benchmark
    from benchHUB.utils.print_config import print_configuration

    # --- Stop Animation ---
    stop_animation_event.set()
    animation_thread.join()
    # Clear the "loading" line
    sys.stdout.write("\r" + " " * 50 + "\r") 
    sys.stdout.flush()

    # --- Argument Parsing ---
    parser = argparse.ArgumentParser(description="Run system benchmarks and contribute to the online leaderboard.")
    parser.add_argument(
        'profile',
        metavar='PROFILE',
        help=f"The benchmark profile to run. Choices: {', '.join(config.CONFIG_PROFILES.keys())}",
        choices=list(config.CONFIG_PROFILES.keys()),
        nargs='?', # Makes the profile argument optional
        default=None
    )
    parser.add_argument('--share', help='Share anonymized results to the online leaderboard.', action='store_true')
    parser.add_argument('--no-share', help='Do not share results to the online leaderboard.', action='store_true')
    args = parser.parse_args()

    # --- Interactive Prompts ---
    profile = args.profile
    if not profile:
        print("Please select a benchmark profile:")
        profiles = list(config.CONFIG_PROFILES.keys())
        for i, p in enumerate(profiles):
            print(f"  {i+1}: {p}")
        while True:
            try:
                choice = int(input(f"Enter choice (1-{len(profiles)}): "))
                if 1 <= choice <= len(profiles):
                    profile = profiles[choice-1]
                    break
                else:
                    print("Invalid choice. Please try again.")
            except ValueError:
                print("Invalid input. Please enter a number.")

    share_results = True
    if args.no_share:
        share_results = False
    elif not args.share and not args.no_share:
        while True:
            choice = input("Share results publicly? (y/n): ").lower()
            if choice in ['y', 'yes']:
                share_results = True
                break
            elif choice in ['n', 'no']:
                share_results = False
                break
            else:
                print("Invalid input. Please enter 'y' or 'n'.")

    # --- Run Benchmarks ---
    results = run_all_benchmarks(profile, config, get_system_info, cpu_benchmark, memory_benchmark, gpu_benchmark, disk_benchmark, ml_benchmark, plot_benchmark, print_configuration)
    if results:
        save_and_submit_results(results, share_results, requests)

def run_all_benchmarks(profile_name, config, get_system_info, cpu_benchmark, memory_benchmark, gpu_benchmark, disk_benchmark, ml_benchmark, plot_benchmark, print_configuration):
    """Orchestrate all benchmarks based on the selected profile."""
    selected_config = config.CONFIG_PROFILES.get(profile_name)
    if not selected_config:
        print(f"Error: Profile '{profile_name}' not found.")
        return None

    print(f"--- Running benchHUB with '{profile_name}' profile ---")
    print_configuration(selected_config)

    print("\nGathering system info...")
    system_info = get_system_info()
    print("System info gathered.")

    print("\nRunning CPU benchmark...")
    cpu_results = cpu_benchmark(selected_config)
    print("CPU benchmark complete.")

    print("\nRunning Memory benchmark...")
    memory_results = memory_benchmark(selected_config)
    print("Memory benchmark complete.")

    print("\nRunning GPU benchmark...")
    gpu_results = gpu_benchmark(selected_config)
    print("GPU benchmark complete.")

    print("\nRunning Disk benchmark...")
    disk_results = disk_benchmark(selected_config)
    print("Disk benchmark complete.")

    print("\nRunning Machine Learning benchmark...")
    ml_results = ml_benchmark(selected_config)
    print("Machine Learning benchmark complete.")

    print("\nRunning Plotting benchmark...")
    plot_results = plot_benchmark(selected_config)
    print("Plotting benchmark complete.")

    results = {
        'system_info': system_info,
        'cpu': cpu_results,
        'memory': memory_results,
        'gpu': gpu_results,
        'disk': disk_results,
        'ml': ml_results,
        'plot': plot_results,
        'config_name': profile_name,
        'uuid': str(uuid.uuid4()),
        'timestamp': datetime.now().isoformat()
    }

    try:
        from benchHUB.reference_index import calculate_reference_index, score_cpu, score_gpu, score_memory
        cpu_score = score_cpu(cpu_results)
        gpu_score = score_gpu(gpu_results)
        memory_score = score_memory(memory_results)
        results['reference_index'] = calculate_reference_index(cpu_score, gpu_score, memory_score)
    except (ImportError, KeyError, TypeError) as e:
        print(f"Could not calculate reference index: {e}")
        results['reference_index'] = 0.0

    return results

def save_and_submit_results(results, share_publicly, requests):
    """Save results locally and optionally submit to the leaderboard."""
    RESULTS_DIR = "results"
    API_URL = os.environ.get("API_URL", "https://benchhub-api.onrender.com")
    
    os.makedirs(RESULTS_DIR, exist_ok=True)
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    local_filename = os.path.join(RESULTS_DIR, f"benchmark_{timestamp}.json")

    with open(local_filename, "w") as f:
        json.dump(results, f, indent=4)
    print(f"\nResults saved locally to: {local_filename}")

    if share_publicly:
        print("\nSubmitting results to the online leaderboard...")
        try:
            def to_serializable(val):
                if isinstance(val, dict): return {k: to_serializable(v) for k, v in val.items()}
                if isinstance(val, list): return [to_serializable(i) for i in val]
                if isinstance(val, (int, float, str, bool)) or val is None: return val
                return str(val)

            serializable_results = to_serializable(results)
            response = requests.post(f"{API_URL}/api/submit", json=serializable_results)
            
            if response.status_code == 200:
                print("Results submitted successfully!")
                print(f"Your benchmark ID is: {results['uuid'][:8]}")
            else:
                print(f"Error submitting results. Status: {response.status_code}, Details: {response.text}")
        except requests.exceptions.RequestException as e:
            print(f"Could not connect to the leaderboard API. Error: {e}")
    
    print("\n--- Benchmark run finished! ---")

if __name__ == '__main__':
    multiprocessing.freeze_support()
    main()
