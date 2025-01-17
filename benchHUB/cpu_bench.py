#cpu_bench.py
import numpy as np
from multiprocessing import Pool, cpu_count
from benchHUB.utils.timing import timing_decorator

# Dictionary to store timing results
timing_results = {}

def cpu_task(_):
    """
    A simple CPU-bound task for parallel processing.

    This task performs a sum of squares for a range of numbers 
    to measure the performance of floating-point operations and 
    parallel task execution.
    """
    return sum([i**2 for i in range(10000)])

@timing_decorator(n_runs=3, use_median=True, timings=timing_results)
def floating_point_operations(array_size: int):
    """Perform a floating-point operation benchmark."""
    x = np.random.rand(array_size)
    y = np.random.rand(array_size)
    _ = np.dot(x, y)  # Just do the dot product

@timing_decorator(n_runs=3, use_median=True, timings=timing_results)
def parallel_processing():
    """Test multi-core performance using multiprocessing."""
    with Pool(cpu_count()) as pool:
        pool.map(cpu_task, range(cpu_count()))

def cpu_benchmark(n_runs: int = 3, array_size: int = 1_000_000):
    """
    Run CPU benchmarks.

    This function executes the following benchmarks:
      1. Floating-point operations.
      2. Parallel processing.
    
    Timing results are automatically captured in `timing_results`.

    Args:
        array_size (int): Size of the arrays for floating-point operations.

    Returns:
        dict: A dictionary with timing results for each benchmark.
    """
    # Run benchmarks
    print("Starting floating-point operation benchmark...")
    floating_point_operations(array_size)

    print("Starting parallel processing benchmark...")
    parallel_processing()

    # Return captured timing results
    return timing_results
