# gpu_bench.py
from benchHUB.utils.timing import timing_decorator

def gpu_benchmark(config: dict):
    """
    Perform GPU benchmarks using parameters from a configuration dictionary.
    """
    timing_results = {}

    @timing_decorator(timings=timing_results)
    def gpu_tensor_operations(matrix_shape):
        import torch
        device = (
            torch.device('cuda') if torch.cuda.is_available()
            else torch.device('mps') if hasattr(torch.backends, 'mps') and torch.backends.mps.is_available()
            else torch.device('cpu')
        )
        if device.type == 'cpu':
            raise RuntimeError("No GPU backend available (CUDA or MPS).")
        x = torch.rand(matrix_shape, device=device)
        y = torch.rand(matrix_shape, device=device)
        _ = torch.matmul(x, y)

    @timing_decorator(timings=timing_results)
    def gpu_tiny_training_loop(epochs: int = 2):
        import torch
        device = (
            torch.device('cuda') if torch.cuda.is_available()
            else torch.device('mps') if hasattr(torch.backends, 'mps') and torch.backends.mps.is_available()
            else torch.device('cpu')
        )
        if device.type == 'cpu':
            return
        model = torch.nn.Linear(100, 1).to(device)
        optimizer = torch.optim.Adam(model.parameters(), lr=0.001)
        criterion = torch.nn.MSELoss()
        X = torch.rand(1000, 100, device=device)
        y = torch.rand(1000, 1, device=device)
        for _ in range(epochs):
            optimizer.zero_grad()
            pred = model(X)
            loss = criterion(pred, y)
            loss.backward()
            optimizer.step()

    matrix_shape = config.get("GPU_MATRIX_SHAPE", (4096, 4096))
    n_runs = config.get("N_RUNS", 3)

    gpu_tensor_operations.n_runs = n_runs
    gpu_tiny_training_loop.n_runs = n_runs

    try:
        print("Starting GPU tensor operations benchmark...")
        gpu_tensor_operations(matrix_shape)
        print("Starting GPU training loop benchmark...")
        gpu_tiny_training_loop()
        return timing_results
    except (ImportError, RuntimeError) as e:
        print(f"GPU benchmark failed: {e}")
        return {"tensor_operations": 0, "tiny_training_loop": 0}