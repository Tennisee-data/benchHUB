# # disk_bench.py
# import os
# import psutil
# import numpy as np
# import time
# import statistics
# 
# def disk_write_read(file_size: int):
#     """
#     Write and read a temporary file to benchmark disk performance.
# 
#     Args:
#         file_size (int): The size (in bytes) of the file to be written.
# 
#     Returns:
#         tuple: A tuple (write_time, read_time) indicating the time
#                taken to write and read the file respectively.
# 
#     Raises:
#         ValueError: If there is not enough disk space for the test.
#     """
#     file_name = "temp_benchmark_file"
#     if psutil.disk_usage(".").free < file_size:
#         raise ValueError("Not enough disk space.")
# 
#     # Write test
#     start_write = time.time()
#     with open(file_name, 'wb') as f:
#         f.write(np.random.bytes(file_size))
#     write_time = time.time() - start_write
# 
#     # Read test
#     start_read = time.time()
#     with open(file_name, 'rb') as f:
#         _ = f.read()
#     read_time = time.time() - start_read
# 
#     if os.path.exists(file_name):
#         os.remove(file_name)
# 
#     return write_time, read_time
# 
# def disk_benchmark(n_runs: int = 3, file_size: int = 50_000_000):
#     """
#     Run the disk write/read benchmark multiple times and compute the median time.
# 
#     Args:
#         n_runs (int): Number of benchmark iterations. Defaults to 3.
#         file_size (int): The size (in bytes) of the file to be written. 
#                          Defaults to 50,000,000 bytes (≈50 MB).
# 
#     Returns:
#         dict: A dictionary containing median write and read times.
#     """
#     write_times = []
#     read_times = []
#     for _ in range(n_runs):
#         w, r = disk_write_read(file_size)
#         write_times.append(w)
#         read_times.append(r)
# 
#     return {
#         'write_time': statistics.median(write_times),
#         'read_time': statistics.median(read_times)
#     }
# 
# if __name__ == "__main__":
#     results = disk_benchmark()
#     print("Disk Benchmark Results:")
#     print(results)


# disk_bench.py
import os
import psutil
import numpy as np
import time
import statistics

from benchHUB.utils.timing import timing_decorator  # or wherever your decorator is

@timing_decorator(n_runs=1, use_median=True)  # n_runs=1 because disk_benchmark loops anyway
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

def disk_benchmark(n_runs: int = 3, file_size: int = 50_000_000):
    """
    Run the disk write/read benchmark multiple times and compute the median time.
    """
    write_times = []
    read_times = []
    for _ in range(n_runs):
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

