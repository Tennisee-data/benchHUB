# benchHUB/reference_index.py

# Define weights for the reference index calculation
CPU_WEIGHT = 0.4
GPU_WEIGHT = 0.4
MEMORY_WEIGHT = 0.2

def calculate_reference_index(cpu_score, gpu_score, memory_score):
    """
    Calculate the overall reference index based on individual scores.
    """
    # The scores are already weighted inverses, so we just sum them up.
    # A higher score is better.
    return (cpu_score + gpu_score + memory_score) * 1000 # Scale for a more readable number

def score_cpu(cpu_results):
    """
    Calculate a score for the CPU based on benchmark results.
    The prime calculation is a good proxy for single-core performance.
    """
    try:
        # Lower time is better, so we take the inverse.
        time = cpu_results.get('calculate_primes')
        if time is None or time == 0:
            return 0
        return (1.0 / time) * CPU_WEIGHT
    except (TypeError, KeyError):
        return 0

def score_gpu(gpu_results):
    """
    Calculate a score for the GPU based on benchmark results.
    Tensor operations are a core measure of GPU throughput.
    """
    try:
        # Handle cases where GPU is not available
        if isinstance(gpu_results, str) or not gpu_results:
            return 0
        # Try both key formats
        time = gpu_results.get('tensor_operations') or gpu_results.get('gpu_tensor_operations')
        if time is None or time == 0:
            return 0
        return (1.0 / time) * GPU_WEIGHT
    except (TypeError, KeyError):
        return 0

def score_memory(memory_results):
    """
    Calculate a score for the memory based on benchmark results.
    Bandwidth is a key performance indicator for memory.
    """
    try:
        # Try both key formats
        time = memory_results.get('bandwidth') or memory_results.get('memory_bandwidth')
        if time is None or time == 0:
            return 0
        return (1.0 / time) * MEMORY_WEIGHT
    except (TypeError, KeyError):
        return 0