# disk_bench.py
import os
import tempfile
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
        if psutil.disk_usage(".").free < file_size:
            raise ValueError("Not enough disk space.")

        # Use tempfile for secure temp file handling (prevents path traversal risks)
        with tempfile.NamedTemporaryFile(delete=True, prefix="benchhub_disk_") as tmp:
            # Write test
            tmp.write(np.random.bytes(file_size))
            tmp.flush()

            # Read test
            tmp.seek(0)
            _ = tmp.read()

    file_size = config.get("DISK_FILE_SIZE", 25_000_000)
    n_runs = config.get("N_RUNS", 3)

    disk_write_read.n_runs = n_runs

    print("Starting disk I/O benchmark...")
    disk_write_read(file_size)

    return timing_results
