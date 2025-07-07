import pandas as pd
import os
import json

def parse_benchmark_results(results_dir: str) -> pd.DataFrame:
    """
    Parse benchmark results from JSON files, aggregate repeated results, and return a DataFrame.

    Args:
        results_dir (str): Path to the directory containing JSON benchmark results.

    Returns:
        pd.DataFrame: A DataFrame with aggregated benchmark results (medians).
    """
    data = []

    # Iterate through JSON files
    for file in os.listdir(results_dir):
        if file.endswith(".json"):
            filepath = os.path.join(results_dir, file)
            row = {} # Initialize row here
            # Extract timestamp from filename (e.g., benchmark_YYYYMMDD_HHMMSS.json or public_benchmark_YYYYMMDD_HHMMSS.json)
            try:
                # Handle both 'benchmark_' and 'public_benchmark_' prefixes
                if file.startswith("benchmark_"):
                    timestamp_str = file.replace("benchmark_", "").replace(".json", "")
                elif file.startswith("public_benchmark_"):
                    timestamp_str = file.replace("public_benchmark_", "").replace(".json", "")
                else:
                    timestamp_str = file.replace(".json", "") # Fallback for other formats

                row["timestamp"] = pd.to_datetime(timestamp_str, format="%Y%m%d_%H%M%S")
            except ValueError:
                row["timestamp"] = pd.NaT # Not a Time (missing timestamp)
            with open(filepath, "r") as f:
                try:
                    result = json.load(f)

                    # Add system info
                    system_info = result.get("system_info", {})
                    
                    # Extract detailed CPU info
                    cpu_model = "Unknown CPU"
                    cpu_cores = "Unknown Cores"
                    if isinstance(system_info, dict):
                        cpu_info = system_info.get("cpu", {})
                        if isinstance(cpu_info, dict):
                            cpu_model = cpu_info.get("model", "Unknown CPU")
                            cpu_cores = cpu_info.get("cores", "Unknown Cores")

                    # Extract detailed GPU info
                    gpu_names = "Unknown GPU"
                    if isinstance(system_info, dict):
                        gpu_list = system_info.get("gpus", [])
                        if isinstance(gpu_list, list):
                            gpu_names = ", ".join([gpu.get("name", "Unknown GPU") for gpu in gpu_list])
                        elif isinstance(gpu_list, str):
                            gpu_names = gpu_list # Handle cases where gpu info is a string error message
                        
                        if not gpu_names or gpu_names == "Unknown GPU": # Fallback for older GPU info or if pynvml failed
                            torch_gpus = system_info.get("torch_gpus", {})
                            if isinstance(torch_gpus, dict):
                                gpu_names = ", ".join(torch_gpus.get("device_names", ["Unknown GPU"]))
                            elif isinstance(torch_gpus, str):
                                gpu_names = torch_gpus

                    # Extract detailed Memory info
                    total_memory_gb = "Unknown"
                    if isinstance(system_info, dict):
                        memory_info = system_info.get("memory", {})
                        if isinstance(memory_info, dict):
                            total_memory_gb = memory_info.get("total_gb", "Unknown")

                    # Create a unique system_id
                    row["system_id"] = f"{system_info.get("os", "Unknown OS")} | {cpu_model} ({cpu_cores} cores) | {gpu_names} | {total_memory_gb}GB RAM"

                    # Add other system info to row
                    row["OS"] = system_info.get("os", "Unknown")
                    row["CPU_Model"] = cpu_model
                    try:
                        row["CPU_Cores"] = int(cpu_cores)
                    except ValueError:
                        row["CPU_Cores"] = None # Or 0, depending on desired behavior for unknown cores
                    row["Memory_Total_GB"] = total_memory_gb
                    row["GPU_Names"] = gpu_names

                    # Add benchmarks
                    # Explicitly extract and flatten benchmark results
                    # CPU
                    cpu_results = result.get("cpu", {})
                    row["cpu_floating_point_operations"] = cpu_results.get("floating_point_operations", 0.0)
                    row["cpu_parallel_processing"] = cpu_results.get("parallel_processing", 0.0)
                    # Handle older 'floating_point' key if present
                    if "floating_point" in cpu_results:
                        row["cpu_floating_point_operations"] = cpu_results.get("floating_point", 0.0)

                    # Memory
                    memory_results = result.get("memory", {})
                    row["memory_allocation"] = memory_results.get("allocation", 0.0)

                    # GPU
                    gpu_results = result.get("gpu", {})
                    row["gpu_tensor_operations"] = gpu_results.get("tensor_operations", 0.0)
                    row["gpu_tiny_training_loop"] = gpu_results.get("tiny_training_loop", 0.0)
                    # Handle older 'matrix_multiplication' key if present
                    if "matrix_multiplication" in gpu_results:
                        row["gpu_tensor_operations"] = gpu_results.get("matrix_multiplication", 0.0)

                    # Disk
                    disk_results = result.get("disk", {})
                    row["disk_write_time"] = disk_results.get("write_time", 0.0)
                    row["disk_read_time"] = disk_results.get("read_time", 0.0)

                    # ML
                    ml_results = result.get("ml", {})
                    row["ml_create_dataset"] = ml_results.get("timings", {}).get("create_dataset", 0.0)
                    row["ml_run_grid_search"] = ml_results.get("timings", {}).get("run_grid_search", 0.0)
                    row["ml_best_score"] = ml_results.get("best_score", 0.0)
                    # Handle older 'grid_search_time' key if present
                    if "grid_search_time" in ml_results:
                        row["ml_run_grid_search"] = ml_results.get("grid_search_time", 0.0)

                    # Flatten ml_timings and ml_best_params if they exist
                    if "timings" in ml_results and isinstance(ml_results["timings"], dict):
                        for timing_key, timing_value in ml_results["timings"].items():
                            row[f"ml_timings_{timing_key}"] = timing_value
                    if "best_params" in ml_results and isinstance(ml_results["best_params"], dict):
                        for param_key, param_value in ml_results["best_params"].items():
                            row[f"ml_best_params_{param_key}"] = param_value

                    # Plot
                    plot_results = result.get("plot", {})
                    row["plot_generate_scatter_plot"] = plot_results.get("generate_scatter_plot", 0.0)
                    row["plot_animate_sine_wave"] = plot_results.get("animate_sine_wave", 0.0)
                    row["plot_render_large_image"] = plot_results.get("render_large_image", 0.0)
                    # Handle older 'scatter_plot_time', 'animation_time', 'large_image_time' keys if present
                    if "scatter_plot_time" in plot_results:
                        row["plot_generate_scatter_plot"] = plot_results.get("scatter_plot_time", 0.0)
                    if "animation_time" in plot_results:
                        row["plot_animate_sine_wave"] = plot_results.get("animation_time", 0.0)
                    if "large_image_time" in plot_results:
                        row["plot_render_large_image"] = plot_results.get("large_image_time", 0.0)

                    # Reference Index (if present)
                    row["reference_index"] = result.get("reference_index", 0.0)

                    # Append to data list
                    print(f"Processing file: {file}")
                    print(f"Row before append: {row}")
                    data.append(row)

                except Exception as e:
                    print(f"Error reading {file}: {e}")

    # Convert to DataFrame
    df = pd.DataFrame(data)
    print(f"DataFrame before aggregation: {df.head()}")

    # Aggregate by system configuration (median of repeated results)
    group_cols = ["system_id", "OS", "CPU_Model", "CPU_Cores", "GPU_Names", "Memory_Total_GB", "timestamp"]
    agg_df = df.groupby(group_cols).median().reset_index()
    print(f"DataFrame after aggregation: {agg_df.head()}")
    print(f"DataFrame dtypes after aggregation: {agg_df.dtypes}")

    return agg_df
    
if __name__ == "__main__":
    # Define the path to your test results directory
    results_dir = "./results"  # Replace with the actual path to your directory

    if not os.path.exists(results_dir):
        print(f"Results directory '{results_dir}' does not exist.")
    else:
        try:
            # Call the function and store the DataFrame
            df = parse_benchmark_results(results_dir)
            
            # Print the DataFrame to debug
            print("Parsed and Aggregated DataFrame:")
            print(df)
            
            # Optional: Save the DataFrame to a CSV for inspection
            df.to_csv("debug_output.csv", index=False)
            print("DataFrame saved to 'debug_output.csv'")
        except Exception as e:
            print(f"An error occurred: {e}")

