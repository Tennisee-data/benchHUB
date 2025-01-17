# gpu_bench.py
from benchHUB.utils.timing import timing_decorator

# Optional: a global dictionary to store timing results
timing_results = {}

@timing_decorator(n_runs=3, use_median=True, timings=timing_results)
def gpu_tensor_operations(matrix_shape):
    """
    Perform tensor operations on the GPU (or fallback to MPS if available).
    """
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
    _ = torch.matmul(x, y)  # matrix multiplication

@timing_decorator(n_runs=3, use_median=True, timings=timing_results)
def gpu_tiny_training_loop(epochs: int = 2):
    """
    Run a minimal training loop on the GPU (or fallback to MPS if available).
    """
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

def gpu_benchmark(n_runs=3, matrix_shape=(10000, 10000)):
    """
    Perform GPU benchmarks for tensor operations and a small training loop.
    """
    # Just call the decorated functions once; the decorator will handle multiple runs.
    try:
        # The actual calls (the decorator runs them n_runs times each).
        gpu_tensor_operations(matrix_shape)
        gpu_tiny_training_loop()

        # Return the timing results collected by the decorator
        return {
            'tensor_operations': timing_results.get('gpu_tensor_operations'),
            'tiny_training_loop': timing_results.get('gpu_tiny_training_loop')
        }
    except (ImportError, RuntimeError) as e:
        return str(e)

if __name__ == "__main__":
    results = gpu_benchmark()
    print("\nGPU Benchmark Results:")
    print(results)

