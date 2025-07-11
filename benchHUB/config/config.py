# config/config.py
# Contains default configuration variables

# Define different configuration profiles
CONFIG_PROFILES = {
    "light": {
        "N_RUNS": 3,
        "DISK_FILE_SIZE": 25_000_000,          # 25MB
        "CPU_PRIME_LIMIT": 20000,               # Primes up to 20k
        "MEMORY_ARRAY_SIZE_MB": 100,            # 100MB array copy
        "GPU_MATRIX_SHAPE": (4096, 4096),       # 4k matrix
        "ML_N_SAMPLES": 5000,
        "ML_N_FEATURES": 10,
    },
    "standard": {
        "N_RUNS": 3,
        "DISK_FILE_SIZE": 50_000_000,          # 50MB
        "CPU_PRIME_LIMIT": 50000,               # Primes up to 50k
        "MEMORY_ARRAY_SIZE_MB": 250,            # 250MB array copy
        "GPU_MATRIX_SHAPE": (8192, 8192),       # 8k matrix
        "ML_N_SAMPLES": 10000,
        "ML_N_FEATURES": 20,
    },
    "heavy": {
        "N_RUNS": 5,
        "DISK_FILE_SIZE": 100_000_000,         # 100MB
        "CPU_PRIME_LIMIT": 100000,              # Primes up to 100k
        "MEMORY_ARRAY_SIZE_MB": 500,            # 500MB array copy
        "GPU_MATRIX_SHAPE": (10000, 10000),      # 10k matrix
        "ML_N_SAMPLES": 20000,
        "ML_N_FEATURES": 50,
    },
}

DEFAULT_CONFIG_NAME = "standard"