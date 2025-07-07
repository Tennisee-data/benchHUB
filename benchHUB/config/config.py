# config/config.py
# Contains default configuration variables

# Default configuration
N_RUNS_DEFAULT = 3
DISK_FILE_SIZE_DEFAULT = 50_000_000
CPU_ARRAY_SIZE_DEFAULT = 1_000_000
MEMORY_SHAPE_DEFAULT = (10_000, 10_000)
GPU_MATRIX_SHAPE_DEFAULT = (10_000, 10_000)
ANIMATION_FRAMES = 100
IMAGE_SHAPE = (4000, 4000)
PLOT_POINTS_DEFAULT = 100_000

# Define different configuration profiles
CONFIG_PROFILES = {
    "standard": {
        "N_RUNS": 3,
        "DISK_FILE_SIZE": 50_000_000,
        "CPU_ARRAY_SIZE": 1_000_000,
        "MEMORY_SHAPE": (10_000, 10_000),
        "GPU_MATRIX_SHAPE": (10_000, 10_000),
        "ANIMATION_FRAMES": 100,
        "IMAGE_SHAPE": (4000, 4000),
        "PLOT_POINTS": 100_000,
    },
    "light": {
        "N_RUNS": 1,
        "DISK_FILE_SIZE": 10_000_000,
        "CPU_ARRAY_SIZE": 100_000,
        "MEMORY_SHAPE": (1_000, 1_000),
        "GPU_MATRIX_SHAPE": (1_000, 1_000),
        "ANIMATION_FRAMES": 50,
        "IMAGE_SHAPE": (1000, 1000),
        "PLOT_POINTS": 10_000,
    },
    "heavy": {
        "N_RUNS": 5,
        "DISK_FILE_SIZE": 100_000_000,
        "CPU_ARRAY_SIZE": 5_000_000,
        "MEMORY_SHAPE": (20_000, 20_000),
        "GPU_MATRIX_SHAPE": (20_000, 20_000),
        "ANIMATION_FRAMES": 200,
        "IMAGE_SHAPE": (8000, 8000),
        "PLOT_POINTS": 200_000,
    },
}

DEFAULT_CONFIG_NAME = "standard"
