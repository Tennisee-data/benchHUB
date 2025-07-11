# memory_bench.py
import numpy as np
from benchHUB.utils.timing import timing_decorator

# Dictionary for timings
timing_results = {}

@timing_decorator(n_runs=5, use_median=True, timings=timing_results)
def memory_bandwidth(array_size_mb):
    """
    Tests memory bandwidth by copying a NumPy array.
    
    Args:
        array_size_mb (int): The size of the array in megabytes.
    """
    # Create an array of the specified size in MB
    num_elements = int((array_size_mb * 1024 * 1024) / 8)  # 8 bytes for float64
    source_array = np.random.rand(num_elements)
    
    # Perform the copy operation to measure bandwidth
    _ = np.copy(source_array)

def memory_benchmark(config: dict):
    """
    Run memory bandwidth benchmark using parameters from a configuration dictionary.
    
    Args:
        config (dict): A dictionary containing benchmark parameters.
                       Expected keys: 'MEMORY_ARRAY_SIZE_MB', 'N_RUNS'.
    """
    array_size_mb = config.get("MEMORY_ARRAY_SIZE_MB", 100)
    n_runs = config.get("N_RUNS", 5)

    # Update decorator runs
    memory_bandwidth.n_runs = n_runs
    
    # Call the decorated function to get timings
    memory_bandwidth(array_size_mb)
    
    # Create dictionary of results
    return {'bandwidth': timing_results.get('memory_bandwidth', None)}

if __name__ == "__main__":
    # Test "main"
    results = memory_benchmark()
    print("\nMemory Benchmark results:")
    print(results)
