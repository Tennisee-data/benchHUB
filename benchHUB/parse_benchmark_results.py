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
            with open(filepath, "r") as f:
                try:
                    result = json.load(f)

                    # Flatten JSON into a single dictionary
                    row = {}

                    # Add system info
                    system_info = result.get("system_info", {})
                    row["OS"] = system_info.get("os", "Unknown")
                    row["CPU_Count"] = system_info.get("cpu_count", "Unknown")
                    row["Memory"] = system_info.get("memory", "Unknown")
                    row["GPU"] = ", ".join(system_info.get("torch_gpus", {}).get("device_names", ["Unknown"]))

                    # Add benchmarks
                    for category, metrics in result.items():
                        if category not in ["system_info"]:  # Skip system info
                            for key, value in metrics.items():
                                if isinstance(value, (int, float)):  # Include only numeric values
                                    row[f"{category}_{key}"] = value

                    # Append to data list
                    data.append(row)

                except Exception as e:
                    print(f"Error reading {file}: {e}")

    # Convert to DataFrame
    df = pd.DataFrame(data)

    # Aggregate by system configuration (median of repeated results)
    group_cols = ["OS", "CPU_Count", "GPU", "Memory"]
    agg_df = df.groupby(group_cols).median().reset_index()

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

