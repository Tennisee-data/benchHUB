# disk_bench.py
import os
import psutil
import numpy as np
import time
import statistics
from benchHUB.utils.timing import timing_decorator

def disk_benchmark(config: dict):
    """
    Run the disk write/read benchmark multiple times using parameters from a configuration dictionary.
    """
    timing_results = {}

    @timing_decorator(timings=timing_results)
    def disk_write_read(file_size: int):
        file_name = "temp_benchmark_file"
        if psutil.disk_usage(".").free < file_size:
            raise ValueError("Not enough disk space.")
        
        # Write test
        with open(file_name, 'wb') as f:
            f.write(np.random.bytes(file_size))
        
        # Read test
        with open(file_name, 'rb') as f:
            _ = f.read()
        
        if os.path.exists(file_name):
            os.remove(file_name)

    file_size = config.get("DISK_FILE_SIZE", 25_000_000)
    n_runs = config.get("N_RUNS", 3)

    disk_write_read.n_runs = n_runs

    print("Starting disk I/O benchmark...")
    disk_write_read(file_size)

    return timing_results
