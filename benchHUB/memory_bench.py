# memory_bench.py
import numpy as np
from benchHUB.utils.timing import timing_decorator

def memory_benchmark(config: dict):
    """
    Run memory bandwidth benchmark using parameters from a configuration dictionary.
    
    Args:
        config (dict): A dictionary containing benchmark parameters.
                       Expected keys: 'MEMORY_ARRAY_SIZE_MB', 'N_RUNS'.
    """
    timing_results = {}

    @timing_decorator(timings=timing_results)
    def memory_bandwidth(array_size_mb):
        num_elements = int((array_size_mb * 1024 * 1024) / 8)
        source_array = np.random.rand(num_elements)
        _ = np.copy(source_array)

    array_size_mb = config.get("MEMORY_ARRAY_SIZE_MB", 100)
    n_runs = config.get("N_RUNS", 5)

    memory_bandwidth.n_runs = n_runs
    
    print("Starting memory bandwidth benchmark...")
    memory_bandwidth(array_size_mb)
    
    return timing_results