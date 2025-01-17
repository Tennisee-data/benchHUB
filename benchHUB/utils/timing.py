#/utils/timing.py
import time
import statistics
from typing import Callable, Dict

def record_time(func: Callable, n_runs: int = 3, use_median: bool = True, *args, **kwargs) -> float:
    """
    Execute a function multiple times and return the median (or mean) elapsed time.
    """
    times = []
    for _ in range(n_runs):
        start = time.time()
        func(*args, **kwargs)
        times.append(time.time() - start)
    return statistics.median(times) if use_median else statistics.mean(times)

def timing_decorator(n_runs: int = 3, use_median: bool = True, timings: Dict = None):
    """
    A decorator to measure the execution time of a function over multiple runs
    and optionally store the results in a dictionary.
    """
    def decorator(func: Callable):
        def wrapper(*args, **kwargs):
            times = []
            # On stocke le résultat de la fonction
            result = None
            for _ in range(n_runs):
                start = time.time()
                result = func(*args, **kwargs)  # APPEL DE LA FONCTION
                times.append(time.time() - start)
            elapsed_time = statistics.median(times) if use_median else statistics.mean(times)
            
            # Store in dictionary if provided
            if timings is not None:
                timings[func.__name__] = elapsed_time
            
            print(f"{func.__name__} executed in {elapsed_time:.6f} seconds "
                  f"(average of {n_runs} runs)")
            
            # On retourne le résultat de la fonction décorée
            return result
        return wrapper
    return decorator
