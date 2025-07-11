# disk_bench.py
import os
import psutil
import numpy as np
import time
import statistics

from benchHUB.utils.timing import timing_decorator

@timing_decorator(n_runs=1, use_median=True)
def disk_write_read(file_size: int):
    """
    Write and read a temporary file to benchmark disk performance.
    """
    file_name = "temp_benchmark_file"
    if psutil.disk_usage(".").free < file_size:
        raise ValueError("Not enough disk space.")

    # Write test
    start_write = time.time()
    with open(file_name, 'wb') as f:
        f.write(np.random.bytes(file_size))
    write_time = time.time() - start_write

    # Read test
    start_read = time.time()
    with open(file_name, 'rb') as f:
        _ = f.read()
    read_time = time.time() - start_read

    if os.path.exists(file_name):
        os.remove(file_name)

    return write_time, read_time

def disk_benchmark(config: dict):
    """
    Run the disk write/read benchmark multiple times using parameters from a configuration dictionary.
    """
    file_size = config.get("DISK_FILE_SIZE", 25_000_000)
    n_runs = config.get("N_RUNS", 3)

    write_times = []
    read_times = []
    for _ in range(n_runs):
        # The decorator on disk_write_read is set to n_runs=1, so this loop is correct.
        w, r = disk_write_read(file_size)
        write_times.append(w)
        read_times.append(r)

    return {
        'write_time': statistics.median(write_times),
        'read_time': statistics.median(read_times)
    }

if __name__ == "__main__":
    results = disk_benchmark()
    print("Disk Benchmark Results:")
    print(results)