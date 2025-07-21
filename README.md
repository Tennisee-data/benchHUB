# benchHUB

benchHUB is a comprehensive cross-platform benchmarking tool that measures system performance across multiple domains. It features local benchmark execution, a REST API backend, web dashboard, and online leaderboard with score submission.

## Features

- **6 Benchmark Categories**: CPU (prime calculation, parallel processing), GPU (tensor operations, ML training), Memory (bandwidth testing), Disk I/O (read/write operations), Machine Learning (dataset creation, model training), and Plotting (scatter plots, animations, large image rendering)
- **Configurable Intensity Profiles**: Light, Standard, and Heavy benchmark modes for different testing needs
- **Cross-Platform GPU Support**: CUDA (NVIDIA) and MPS (Apple Silicon) with graceful fallback
- **Reference Index Scoring**: Normalized scoring system combining CPU, GPU, and Memory performance
- **Online Leaderboard**: Submit and compare results with other users anonymously
- **Streamlit Dashboard**: Interactive web interface for visualizing and comparing benchmark results
- **REST API**: FastAPI backend for result submission and leaderboard management
- **Modular Architecture**: Extensible codebase for adding custom benchmarks

## Installation

1. Clone the repository:
```bash
git clone https://github.com/Tennisee-data/benchHUB.git
cd benchHUB
```

2. Install the dependencies:
Make sure you have Python 3.8+ installed.
Create a virtual environment and install required packages:

```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\\Scripts\\activate
pip install -r requirements.txt
```

## Configuration Profiles

benchHUB uses three configurable intensity profiles to accommodate different hardware capabilities and time constraints. You can modify these in `benchHUB/config/config.py`:

### Light Profile (Fast execution)
- **N_RUNS**: 3 benchmark iterations
- **DISK_FILE_SIZE**: 25MB for I/O testing
- **CPU_PRIME_LIMIT**: Calculate primes up to 20,000
- **MEMORY_ARRAY_SIZE**: 100MB array operations
- **GPU_MATRIX_SHAPE**: 4096×4096 matrix operations
- **ML_SAMPLES/FEATURES**: 5,000 samples with 10 features

### Standard Profile (Balanced testing - default)
- **N_RUNS**: 3 benchmark iterations
- **DISK_FILE_SIZE**: 50MB for I/O testing
- **CPU_PRIME_LIMIT**: Calculate primes up to 50,000
- **MEMORY_ARRAY_SIZE**: 250MB array operations
- **GPU_MATRIX_SHAPE**: 8192×8192 matrix operations
- **ML_SAMPLES/FEATURES**: 10,000 samples with 20 features

### Heavy Profile (Intensive benchmarking)
- **N_RUNS**: 5 benchmark iterations
- **DISK_FILE_SIZE**: 100MB for I/O testing
- **CPU_PRIME_LIMIT**: Calculate primes up to 100,000
- **MEMORY_ARRAY_SIZE**: 500MB array operations
- **GPU_MATRIX_SHAPE**: 10000×10000 matrix operations
- **ML_SAMPLES/FEATURES**: 20,000 samples with 50 features

## Usage

1. Run benchHUB (from the root benchHUB directory):
```bash
python -m benchHUB.main
```
It executes benchmarks defined in the project and saves results to the results/ directory in JSON format.

2. Visualize Results (from the root benchHUB directory):
To launch the Streamlit dashboard for visualizing benchmark results:
```bash
streamlit run dashboard.py
```
This will parse the JSON files in the results/ directory and provide an interactive UI to analyse and compare metrics.

3. Adding Your Own Tests:
To add a custom test, follow these steps:
- Create a new Python script in the sub directory benchHUB/ (I know the child should not have the parent's name but, it was such a great name...), e.g., custom_bench.py.
- Define your test logic, ensuring the output matches the format expected by the JSON parser.
- Import and integrate the test in main.py to include it in the benchmarking suite.

## Scoring System

benchHUB includes a **Reference Index** scoring system that normalizes benchmark results into comparable scores:

- **Composite Score**: Combines CPU (40%), GPU (40%), and Memory (20%) performance
- **Inverse Timing**: Lower execution times result in higher scores
- **Score Capping**: Final scores are capped under 1000 for better user experience
- **GPU Fallback**: Systems without GPU support gracefully return 0 for GPU scores
- **Anonymous Leaderboard**: Submit results to compare with other users worldwide

The scoring system enables fair comparison across different hardware configurations while maintaining realistic score ranges.

## Database Management

For administrators managing the online leaderboard database, see the comprehensive guide:

📖 **[DATABASE_MANAGEMENT.md](DATABASE_MANAGEMENT.md)**

This guide covers:
- Database cleanup procedures
- Score validation and maintenance  
- Production database administration
- Troubleshooting common issues