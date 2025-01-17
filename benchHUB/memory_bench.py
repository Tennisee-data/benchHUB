# memory_bench.py
import numpy as np
from benchHUB.utils.timing import timing_decorator

# Dictionary for timings
timing_results = {}

@timing_decorator(n_runs=3, use_median=True, timings=timing_results)
def memory_allocation(matrix_shape):
    """Allocate and deallocate a large matrix."""
    x = np.zeros(matrix_shape)
    del x  # Free memory, Python would do it anyway

def memory_benchmark(n_runs: int = 3, matrix_shape=(10000, 10000)):
    # Call the decorated function to get timings
    memory_allocation(matrix_shape)
    
    # Create dictionary of results
    return {'allocation': timing_results.get('memory_allocation', None)}

if __name__ == "__main__":
    # Test "main"
    results = memory_benchmark()
    print("\nMemory Benchmark results:")
    print(results)