#plot_bench.py
from benchHUB.utils.timing import timing_decorator
import numpy as np

# Suppress matplotlib font cache building message
import logging
logging.getLogger('matplotlib.font_manager').setLevel(logging.ERROR)

import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation, FFMpegWriter, PillowWriter

# Timing storage
timing_results = {}

@timing_decorator(n_runs=3, use_median=True, timings=timing_results)
def generate_scatter_plot(points: int):
    """
    Generate and render a scatter plot with the given number of points.
    """
    x = np.random.rand(points)
    y = np.random.rand(points)
    plt.scatter(x, y)
    plt.title("Scatter Plot Benchmark")
    plt.close()

@timing_decorator(n_runs=3, use_median=True, timings=timing_results)
def animate_sine_wave(n_frames: int = 100):
    """
    Create a simple sine wave animation and force it to render by saving.
    """
    # Use non-interactive backend for this function
    plt.switch_backend("Agg")

    fig, ax = plt.subplots()
    x = np.linspace(0, 2 * np.pi, 1000)
    line, = ax.plot(x, np.sin(x))

    def update(frame):
        line.set_ydata(np.sin(x + frame / 10))
        return line,

    # Select writer based on availability
    if FFMpegWriter.isAvailable():
        writer = FFMpegWriter(fps=20)
        extension = "mp4"
    else:
        writer = PillowWriter(fps=20)
        extension = "gif"

    # Save the animation
    ani = FuncAnimation(fig, update, frames=n_frames, blit=True)
    ani.save(f"temp_animation.{extension}", writer=writer)
    plt.close(fig)

@timing_decorator(n_runs=3, use_median=True, timings=timing_results)
def render_large_image(shape=(4000, 4000)):
    """
    Render a large random image and save to file to ensure actual rendering.
    """
    # Use non-interactive backend for this function
    plt.switch_backend("Agg")
    image = np.random.rand(*shape)

    fig, ax = plt.subplots()
    ax.imshow(image, cmap="gray")
    fig.savefig("temp_image.png", dpi=80)  # Force rendering
    plt.close(fig)

def plot_benchmark(
    n_runs: int = 3, 
    points: int = 100000, 
    n_frames: int = 100, 
    image_shape=(4000, 4000),
):
    """
    Run various plotting benchmarks, returning the timing results in a dictionary.
    """
    print("Running scatter plot benchmark...")
    generate_scatter_plot(points=points)

    print("Running sine wave animation benchmark...")
    animate_sine_wave(n_frames=n_frames)

    print("Running large image rendering benchmark...")
    render_large_image(shape=image_shape)

    # Return all captured timing results
    return timing_results
    
    
if __name__ == "__main__":
    results = plot_benchmark(n_runs=3, points=100000, n_frames=100, image_shape=(4000, 4000))
    print("\nPlot Benchmark Results:")
    print(results)