# config/system_info.py
import platform
import psutil
import GPUtil

def get_system_info():
    """
    Collect and return system information (OS, CPU, memory, GPU, etc.).
    """
    system_info = {
        'os': platform.system(),
        'os_version': platform.version(),
        'architecture': platform.architecture()[0],
        'cpu_count': psutil.cpu_count(logical=True),
        'memory': f"{round(psutil.virtual_memory().total / (1024 ** 3), 2)} GB"
    }
    try:
        gpu_info = GPUtil.getGPUs()
        system_info['gpus'] = [
            {
                'name': gpu.name,
                'memory': f"{gpu.memoryTotal} MB",
                'driver': gpu.driver
            }
            for gpu in gpu_info
        ]
    except Exception:
        system_info['gpus'] = "Could not retrieve GPU information via GPUtil."

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
