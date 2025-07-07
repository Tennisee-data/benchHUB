# benchHUB/reference_index.py

# Define weights for the reference index calculation
CPU_WEIGHT = 0.4
GPU_WEIGHT = 0.4
MEMORY_WEIGHT = 0.2

def calculate_reference_index(cpu_score, gpu_score, memory_score):
    """
    Calculate the overall reference index based on individual scores.
    """
    reference_index = (
        CPU_WEIGHT * cpu_score +
        GPU_WEIGHT * gpu_score +
        MEMORY_WEIGHT * memory_score
    )
    return reference_index

def score_cpu(cpu_results):
    """
    Calculate a score for the CPU based on benchmark results.
    """
    # Simple scoring: inverse of execution time
    return 1.0 / cpu_results['floating_point_operations']

def score_gpu(gpu_results):
    """
    Calculate a score for the GPU based on benchmark results.
    """
    # Simple scoring: inverse of execution time
    return 1.0 / gpu_results['tensor_operations']

def score_memory(memory_results):
    """
    Calculate a score for the memory based on benchmark results.
    """
    # Simple scoring: inverse of execution time
    return 1.0 / memory_results['allocation']
