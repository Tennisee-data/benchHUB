# cpu_bench.py
import numpy as np
from multiprocessing import Pool, cpu_count
from benchHUB.utils.timing import timing_decorator

def cpu_task(_):
    """
    A simple CPU-bound task for parallel processing.
    This task performs a sum of squares for a range of numbers.
    """
    return sum([i**2 for i in range(10000)])

def cpu_benchmark(config: dict):
    """
    Run CPU benchmarks using parameters from a configuration dictionary.

    Args:
        config (dict): A dictionary containing benchmark parameters.
                       Expected keys: 'CPU_PRIME_LIMIT', 'N_RUNS'.

    Returns:
        dict: A dictionary with timing results for each benchmark.
    """
    # Use a local dictionary to ensure results are isolated.
    timing_results = {}

    # Create local, decorated versions of the functions
    @timing_decorator(timings=timing_results)
    def calculate_primes(max_number: int):
        primes = []
        for num in range(2, max_number + 1):
            is_prime = True
            for i in range(2, int(num**0.5) + 1):
                if num % i == 0:
                    is_prime = False
                    break
            if is_prime:
                primes.append(num)
        return primes

    @timing_decorator(timings=timing_results)
    def parallel_processing():
        with Pool(cpu_count()) as pool:
            pool.map(cpu_task, range(cpu_count()))

    prime_limit = config.get("CPU_PRIME_LIMIT", 20000)
    n_runs = config.get("N_RUNS", 3)

    # Update decorator runs
    calculate_primes.n_runs = n_runs
    parallel_processing.n_runs = n_runs

    # Run benchmarks
    print("Starting prime calculation benchmark...")
    calculate_primes(prime_limit)

    print("Starting parallel processing benchmark...")
    parallel_processing()

    # Return captured timing results
    return timing_results