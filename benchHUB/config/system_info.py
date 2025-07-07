# config/system_info.py
import platform
import psutil
import GPUtil
import cpuinfo
import pynvml

def get_system_info():
    """
    Collect and return detailed system information (OS, CPU, memory, GPU, etc.).
    """
    # CPU Info
    cpu_info = cpuinfo.get_cpu_info()
    try:
        cpu_freq = psutil.cpu_freq()
    except FileNotFoundError:
        cpu_freq = None

    system_info = {
        'os': platform.system(),
        'os_version': platform.version(),
        'architecture': platform.architecture()[0],
        'cpu': {
            'model': cpu_info.get('brand_raw', 'N/A'),
            'cores': psutil.cpu_count(logical=False),
            'threads': psutil.cpu_count(logical=True),
            'frequency_mhz': cpu_freq.current if cpu_freq else 'N/A',
            'l2_cache_size': cpu_info.get('l2_cache_size', 'N/A'),
            'l3_cache_size': cpu_info.get('l3_cache_size', 'N/A'),
        },
        'memory': {
            'total_gb': round(psutil.virtual_memory().total / (1024 ** 3), 2),
            'available_gb': round(psutil.virtual_memory().available / (1024 ** 3), 2),
            'used_percent': psutil.virtual_memory().percent,
        }
    }

    # GPU Info
    try:
        pynvml.nvmlInit()
        gpu_count = pynvml.nvmlDeviceGetCount()
        gpus = []
        for i in range(gpu_count):
            handle = pynvml.nvmlDeviceGetHandleByIndex(i)
            gpu_info = {
                'name': pynvml.nvmlDeviceGetName(handle),
                'memory_total_mb': pynvml.nvmlDeviceGetMemoryInfo(handle).total / (1024**2),
                'power_limit_w': pynvml.nvmlDeviceGetEnforcedPowerLimit(handle) / 1000.0,
                'driver_version': pynvml.nvmlSystemGetDriverVersion()
            }
            gpus.append(gpu_info)
        system_info['gpus'] = gpus
        pynvml.nvmlShutdown()
    except pynvml.NVMLError:
        system_info['gpus'] = "NVIDIA GPU not found or pynvml failed."

    # Torch detection
    try:
        import torch
        if torch.cuda.is_available():
            system_info['torch_gpus'] = {
                'backend': 'CUDA',
                'device_count': torch.cuda.device_count(),
                'device_names': [torch.cuda.get_device_name(i) for i in range(torch.cuda.device_count())]
            }
        elif torch.backends.mps.is_available():
            system_info['torch_gpus'] = {
                'backend': 'MPS',
                'device_count': 1,
                'device_names': ['Apple M-series GPU']
            }
        else:
            system_info['torch_gpus'] = "No supported GPU backend available."
    except ImportError:
        system_info['torch_gpus'] = "Torch not installed."

    return system_info
