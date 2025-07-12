# benchHUB

benchHUB is a Python-based project to parse, aggregate, and visualize system 
and performance benchmarks. It includes a Streamlit dashboard to display and compare results.

## Features

- Get timings for GPU, CPU, disk r/w operations, Machine Learning tasks, plotting complex graphs
- Add more tests or tweak current functions
- Parse JSON benchmark results and aggregate data.
- Visualize and compare metrics through a Streamlit dashboard.
- Designed for extensibility with a modular codebase.
- Anticipated a database to store results (not implemented)

## Installation

1. Clone the repository:
```bash
   git clone https://github.com/Tennisee-data/benchHUB.git
   cd benchHUB
   
2. Install the dependencies:
Make sure you have Python 3.8+ installed.
Create a virtual environment and install required packages:

python -m venv venv
source venv/bin/activate  # On Windows: venv\\Scripts\\activate
pip install -r requirements.txt
   
## Configuration Defaults
The following are the default parameters for `benchHUB`. You can modify them directly in `config/config.py` to suit your system:

- **N_RUNS_DEFAULT**: The default number of runs for each benchmark (default: `3`).
Useful for averaging or finding the median of multiple runs.
- **DISK_FILE_SIZE_DEFAULT**: File size for disk benchmark in bytes (default: `50,000,000`)
This sets the size of the file to test disk performance, likely in bytes (~50 MB).
This is reasonable for most systems but can be scaled based on hardware capabilities.
- **CPU_ARRAY_SIZE_DEFAULT**: Array size for CPU floating-point operations (default: `1,000,000`)
This sets the size of the array for CPU floating-point operations (dot product).
The dot product involves 𝑛ˆ3 floating-point operations for square matrices of size n × n.
- **MEMORY_SHAPE_DEFAULT**: Shape of matrix for memory benchmarks (default: `(10,000, 10,000)`)
The shape of the matrix for memory benchmarks.
This results in a matrix with 100 million elements (~800 MB for float64 data type).
- **GPU_MATRIX_SHAPE_DEFAULT**: Shape of matrix for GPU benchmarks (default: `(10,000, 10,000)`)
The shape of the matrix for GPU benchmarks.
GPU computations often handle large matrices better than CPUs, but this still consumes ~800 MB of VRAM.
- **ANIMATION_FRAMES**: Number of frames for animation benchmark (default: `100`)
Number of frames for animation-based benchmarking (plot-related tasks).
Balanced for testing rendering performance without taking excessive time.
- **IMAGE_SHAPE**: Shape of rendered image for plotting benchmark (default: `(4000, 4000)`)
Shape of the generated image for testing rendering or plotting performance.
Results in ~64 MB of data for float64.
- **PLOT_POINTS_DEFAULT**: Number of points in scatter plot benchmark (default: `100,000`)
Number of points for scatter plot benchmarks.
Large enough to test rendering performance but manageable for most systems.

```python
CPU_ARRAY_SIZE_DEFAULT = 500_000  # Example: Decrease array size for CPU benchmark to avoid memory bottlenecks

## Usage
1. Run benchHUB (from the root benchHUB directory):
```bash
python -m benchHUB.main
It executes benchmarks defined in the project and saves results to the results/ directory in JSON format.

2. Visualize Results (from the root benchHUB directory)
To launch the Streamlit dashboard for visualizing benchmark results:
```bash
streamlit run dashboard.py
This will parse the JSON files in the results/ directory and provide an interactive UI to analyse and compare metrics.

3. Adding Your Own Tests
To add a custom test, follow these steps:
Create a new Python script in the sub directory benchHUB/ (I know the child should not have the parent's name but, it was such a great name...), e.g., custom_bench.py.
Define your test logic, ensuring the output matches the format expected by the JSON parser.
Import and integrate the test in main.py to include it in the benchmarking suite.

## Database Management

For administrators managing the online leaderboard database, see the comprehensive guide:

📖 **[DATABASE_MANAGEMENT.md](DATABASE_MANAGEMENT.md)**

This guide covers:
- Database cleanup procedures
- Score validation and maintenance  
- Production database administration
- Troubleshooting common issues