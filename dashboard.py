import streamlit as st
import pandas as pd
import requests
import json
import os
from benchHUB.parse_benchmark_results import parse_benchmark_results
from benchHUB.config import config # Import config to access profiles

# Define path to results directory
RESULTS_DIR = "results"
print(f"Current working directory: {os.getcwd()}")
API_URL = "http://127.0.0.1:8000"

# Parse benchmark results
st.title("Benchmark Comparison Dashboard")
st.write("Parsing results from:", RESULTS_DIR)

df = parse_benchmark_results(RESULTS_DIR)

# Debugging: Display the raw DataFrame
st.write("### Raw Benchmark Data")
st.dataframe(df)

# Check if DataFrame is empty
if df.empty:
    st.warning("No benchmark results found. Please run some benchmarks first.")
else:
    # Ensure timestamp is datetime and sort
    df['timestamp'] = pd.to_datetime(df['timestamp'])
    df = df.sort_values(by='timestamp')

    # Sidebar for filtering
    st.sidebar.title("Filters")

    # Filter by configuration profile
    config_profiles = ["All"] + list(config.CONFIG_PROFILES.keys())
    selected_config_profile = st.sidebar.selectbox("Select Configuration Profile", config_profiles)

    # Apply configuration profile filter
    if selected_config_profile != "All":
        df = df[df['config_name'] == selected_config_profile]
    
    # Filter by system
    systems = df['system_id'].unique()
    selected_system = st.sidebar.selectbox("Select System", systems)
    
    # Filter by benchmark type
    benchmark_types = ['cpu', 'memory', 'gpu', 'disk', 'ml', 'plot']
    selected_benchmark = st.sidebar.selectbox("Select Benchmark Type", benchmark_types)
    
    # Filtered DataFrame
    filtered_df = df[df['system_id'] == selected_system]
    
    # Display selected benchmark data
    st.write(f"### {selected_benchmark.upper()} Benchmark Results for {selected_system}")
    
    # Extract relevant columns for the selected benchmark
    benchmark_cols = [col for col in df.columns if col.startswith(selected_benchmark)]
    
    if not benchmark_cols:
        st.warning(f"No data available for benchmark type: {selected_benchmark}")
    else:
        # Display data in a table
        st.dataframe(filtered_df[['timestamp'] + benchmark_cols])
        
        # Plotting results
        st.write("### Performance Over Time")
        
        # Allow user to select a metric to plot
        metric_to_plot = st.selectbox("Select metric to plot", benchmark_cols)
        
        if metric_to_plot:
            # Ensure the metric column is numeric
            filtered_df[metric_to_plot] = pd.to_numeric(filtered_df[metric_to_plot], errors='coerce')
            
            # Drop rows where the metric is NaN (e.g., if conversion failed)
            plot_data = filtered_df.dropna(subset=[metric_to_plot])

            print(f"Plotting data for {metric_to_plot}:\n{plot_data.set_index('timestamp')[metric_to_plot]}")
            if not plot_data.empty:
                st.line_chart(plot_data.set_index('timestamp')[metric_to_plot])
            else:
                st.warning(f"No valid numeric data to plot for {metric_to_plot}.")

# Leaderboard
st.title("Online Leaderboard")
try:
    response = requests.get(f"{API_URL}/api/leaderboard")
    if response.status_code == 200:
        leaderboard_data = response.json()
        
        # Flatten the JSON strings in the leaderboard data
        processed_leaderboard_data = []
        for record in leaderboard_data:
            flat_record = {"id": record["id"], "reference_index": record["reference_index"], "config_name": record.get("config_name", "Unknown")}
            
            # Parse and flatten system_info
            system_info = json.loads(record["system_info"])
            flat_record["OS"] = system_info.get("os", "Unknown")
            flat_record["CPU_Model"] = system_info.get("cpu", {}).get("model", "Unknown CPU")
            flat_record["GPU_Names"] = system_info.get("gpus", "Unknown GPU")
            flat_record["Memory_Total_GB"] = system_info.get("memory", {}).get("total_gb", "Unknown")

            # Parse and flatten other benchmark results
            for key in ["cpu", "memory", "gpu", "disk", "ml", "plot"]:
                if key in record and record[key] is not None:
                    try:
                        metrics = json.loads(record[key])
                        if isinstance(metrics, dict):
                            if key == "ml":
                                # Special handling for ML benchmark to flatten timings and best_params
                                if "timings" in metrics and isinstance(metrics["timings"], dict):
                                    for timing_key, timing_value in metrics["timings"].items():
                                        flat_record[f"ml_timings_{timing_key}"] = timing_value
                                if "best_params" in metrics and isinstance(metrics["best_params"], dict):
                                    for param_key, param_value in metrics["best_params"].items():
                                        flat_record[f"ml_best_params_{param_key}"] = param_value
                                # Add other top-level ML metrics
                                for metric_name, value in metrics.items():
                                    if metric_name not in ["timings", "best_params"]:
                                        flat_record[f"{key}_{metric_name}"] = value
                            else:
                                for metric_name, value in metrics.items():
                                    flat_record[f"{key}_{metric_name}"] = value
                        else:
                            flat_record[key] = metrics # For cases where it's a simple value
                    except json.JSONDecodeError:
                        flat_record[key] = record[key] # Keep as is if not valid JSON
                else:
                    flat_record[key] = None # Ensure key exists even if value is None

            processed_leaderboard_data.append(flat_record)

        leaderboard_df = pd.DataFrame(processed_leaderboard_data)

        # Filter leaderboard by configuration profile
        leaderboard_config_profiles = ["All"] + list(leaderboard_df['config_name'].unique())
        selected_leaderboard_config_profile = st.selectbox("Filter Leaderboard by Configuration Profile", leaderboard_config_profiles)

        if selected_leaderboard_config_profile != "All":
            leaderboard_df = leaderboard_df[leaderboard_df['config_name'] == selected_leaderboard_config_profile]

        st.dataframe(leaderboard_df)
    else:
        st.error("Could not retrieve leaderboard data from the API.")
except requests.exceptions.ConnectionError:
    st.error("Could not connect to the leaderboard API. Please make sure the API is running.")
