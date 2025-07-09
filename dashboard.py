import streamlit as st
import pandas as pd
import requests
import json
import os
from benchHUB.parse_benchmark_results import parse_benchmark_results
from benchHUB.config import config

# --- Page Configuration ---
st.set_page_config(layout="wide", page_title="benchHUB Leaderboard")

# --- Environment and Constants ---
RESULTS_DIR = "results"
API_URL = os.environ.get("API_URL", "http://127.0.0.1:8000")

# --- Custom CSS for Styling ---
def load_css():
    css = """
    <style>
        /* General Body */
        .stApp {
            background-color: #1E1E1E;
            color: #FFFFFF;
        }
        /* Card styling */
        .card {
            border: 1px solid #4A4A4A;
            border-radius: 10px;
            padding: 20px;
            margin: 10px 0;
            background-color: #2C2C2C;
            box-shadow: 0 4px 8px rgba(0, 0, 0, 0.2);
            transition: transform 0.2s;
        }
        .card:hover {
            transform: scale(1.02);
        }
        /* Highlighted card for search result */
        .highlighted-card {
            border: 2px solid #1E90FF;
            background-color: #333A44;
        }
        /* Rank styling */
        .rank {
            font-size: 2.5em;
            font-weight: bold;
            color: #1E90FF;
            text-align: center;
        }
        /* Score styling */
        .score {
            font-size: 2em;
            font-weight: bold;
            color: #FFFFFF;
            text-align: right;
        }
        /* System info styling */
        .system-info {
            font-size: 1.1em;
            color: #D3D3D3;
        }
        .system-info-icon {
            font-size: 1.5em;
            margin-right: 10px;
        }
        /* UUID styling */
        .uuid {
            font-size: 0.8em;
            color: #808080;
            font-family: monospace;
        }
        /* Section headers */
        h1, h2, h3 {
            color: #FFFFFF;
        }
    </style>
    """
    st.markdown(css, unsafe_allow_html=True)

# --- Main Application ---
load_css()

# --- Header and Logo ---
col1, col2, col3 = st.columns([2, 6, 2])
with col2:
    st.image("benchHUB.jpg", use_column_width=True)

st.title("🏆 Online Leaderboard")

# --- Leaderboard Section ---
try:
    response = requests.get(f"{API_URL}/api/leaderboard")
    response.raise_for_status()  # Raise an exception for bad status codes
    leaderboard_data = response.json()

    if not leaderboard_data:
        st.info("The leaderboard is currently empty. Submit your benchmark to get started!")
    else:
        # Create a DataFrame for easier filtering
        processed_data = []
        for record in leaderboard_data:
            system_info = json.loads(record.get("system_info", "{}"))
            
            # Correctly parse nested system info
            cpu_info = system_info.get("cpu", {})
            mem_info = system_info.get("memory", {})
            
            # Handle different possible GPU info structures
            if "gpus" in system_info and isinstance(system_info["gpus"], list) and system_info["gpus"]:
                gpu_model = ", ".join([gpu.get("name", "N/A") for gpu in system_info["gpus"]])
            elif "torch_gpus" in system_info and isinstance(system_info["torch_gpus"], dict):
                gpu_model = ", ".join(system_info["torch_gpus"].get("device_names", ["N/A"]))
            else:
                gpu_model = "N/A"

            processed_data.append({
                "id": record["id"],
                "reference_index": record["reference_index"],
                "config_name": record.get("config_name", "standard"),
                "uuid": record.get("uuid", "N/A"),
                "cpu_model": cpu_info.get("model", "Unknown CPU"),
                "gpu_model": gpu_model,
                "memory_total": f"{mem_info.get('total_gb', 'N/A')} GB"
            })
        
        leaderboard_df = pd.DataFrame(processed_data)
        
        # --- Sidebar Filters for Leaderboard ---
        st.sidebar.title("Leaderboard Filters")
        
        # Define the desired order for profiles
        profile_order = ["heavy", "standard", "light"]
        
        # Get profiles present in the data
        present_profiles = leaderboard_df['config_name'].unique()
        
        # Sort the available profiles according to the desired order
        available_profiles = [p for p in profile_order if p in present_profiles]
        
        # Create the list for the selectbox
        config_profiles = ["All"] + available_profiles
        selected_config = st.sidebar.selectbox("Filter by Configuration", config_profiles)

        uuid_filter = st.sidebar.text_input("Filter by UUID (or partial UUID)")

        # --- Display Logic ---
        
        # Function to display a single result card
        def display_card(rank, data_row, is_highlighted=False):
            score_formatted = f"{int(data_row['reference_index']):,}".replace(",", " ")
            card_class = "card highlighted-card" if is_highlighted else "card"
            st.markdown(f'<div class="{card_class}">', unsafe_allow_html=True)
            col1, col2, col3 = st.columns([1, 4, 2])

            with col1:
                st.markdown(f'<p class="rank">{rank}</p>', unsafe_allow_html=True)

            with col2:
                st.markdown(f"""
                    <div class="system-info">
                        <span><span class="system-info-icon">💻</span> {data_row['cpu_model']}</span><br>
                        <span><span class="system-info-icon">🎨</span> {data_row['gpu_model']}</span><br>
                        <span><span class="system-info-icon">💾</span> {data_row['memory_total']}</span>
                    </div>
                    <div class="uuid">UUID: {data_row['uuid'][:8]}</div>
                """, unsafe_allow_html=True)

            with col3:
                st.markdown(f'<p class="score">{score_formatted}</p>', unsafe_allow_html=True)
                st.markdown('<p class="score-label" style="text-align: right; color: #808080;">Score</p>', unsafe_allow_html=True)

            st.markdown('</div>', unsafe_allow_html=True)

        # Filter by UUID first if provided
        if uuid_filter:
            search_result_df = leaderboard_df[leaderboard_df['uuid'].str.startswith(uuid_filter, na=False)]
            
            if search_result_df.empty:
                st.warning("No results found for this UUID.")
            else:
                # Get the first found result's info
                result_row = search_result_df.iloc[0]
                result_config = result_row['config_name']
                
                st.subheader(f"Search Result in '{result_config.capitalize()}' Configuration")

                # Get the full leaderboard for that config and sort it
                config_df = leaderboard_df[leaderboard_df['config_name'] == result_config].sort_values(
                    by='reference_index', ascending=False
                ).reset_index(drop=True)

                # Find the index of our result
                result_index = config_df[config_df['uuid'] == result_row['uuid']].index[0]
                
                # Define the context window
                context = 2
                start_index = max(0, result_index - context)
                end_index = min(len(config_df), result_index + context + 1)
                
                # Get the slice of the leaderboard to display
                contextual_df = config_df.iloc[start_index:end_index]
                
                for i, row in contextual_df.iterrows():
                    rank = i + 1
                    is_highlighted = (row['uuid'] == result_row['uuid'])
                    display_card(rank=rank, data_row=row, is_highlighted=is_highlighted)

        # Display by configuration if no UUID search
        elif selected_config == "All":
            for profile in available_profiles:
                st.subheader(f"{profile.capitalize()} Configuration")
                profile_df = leaderboard_df[leaderboard_df['config_name'] == profile].sort_values(by='reference_index', ascending=False).reset_index(drop=True)
                for i, row in profile_df.iterrows():
                    display_card(rank=i + 1, data_row=row)
                st.markdown("---")
        
        else: # A specific configuration is selected
            st.subheader(f"{selected_config.capitalize()} Configuration")
            display_df = leaderboard_df[leaderboard_df['config_name'] == selected_config].sort_values(by='reference_index', ascending=False).reset_index(drop=True)
            for i, row in display_df.iterrows():
                display_card(rank=i + 1, data_row=row)



except requests.exceptions.RequestException as e:
    st.error(f"Could not connect to the leaderboard API. Please ensure it's running. Error: {e}")


# --- Local Benchmark Analysis Section ---
st.markdown("---")
st.header("🔬 Analyze Local Benchmark Files")

try:
    df_local = parse_benchmark_results(RESULTS_DIR)

    if df_local.empty:
        st.warning("No local benchmark JSON files found in the 'results/' directory.")
    else:
        st.dataframe(df_local)
        st.info("More detailed local analysis features can be added here.")

except Exception as e:
    st.error(f"Failed to parse local benchmark files. Error: {e}")

# --- Downloads Section ---
st.markdown("---")
st.header("📥 Get the Benchmarker")
st.write("Visit our official download page to get the command-line tool for your operating system. You can also view the source code and instructions there.")
st.markdown('<a href="https://tennisee-data.github.io/benchHUB_web/" target="_blank"><button style="width:100%; padding: 10px; background-color: #1E90FF; color: white; border: none; border-radius: 5px; font-size: 1.2em;">Go to Download Page</button></a>', unsafe_allow_html=True)


# --- Methodology Section ---
st.markdown("---")
st.header("⚙️ Our Methodology")
st.write(
    """
    Our goal is to provide a standardized, transparent, and reliable way to measure and compare computer performance across different systems and configurations. 
    This is how we do it.
    """
)

st.subheader("1. Core Performance Tests")
st.write(
    """
    The benchmark suite is composed of several micro-tests, each designed to stress a specific component of your system. The time taken to complete each test is measured precisely.
    - **CPU (Floating Point)**: Measures the speed of floating-point arithmetic, a cornerstone of scientific and multimedia tasks.
    - **CPU (Parallel Processing)**: Tests the CPU's ability to handle multiple tasks simultaneously, crucial for modern applications.
    - **GPU (Tensor Operations)**: Stresses the GPU with matrix multiplications, fundamental to machine learning and 3D graphics.
    - **Memory (Allocation)**: Measures the speed of allocating and freeing large blocks of system memory.
    - **Disk (Read/Write)**: Tests the sequential read and write speed of your primary storage drive.
    - **Machine Learning (Grid Search)**: Simulates a real-world ML model tuning task to evaluate a combination of CPU, GPU, and memory performance.
    - **Plotting (Complex Visuals)**: Measures the time to generate and render complex data visualizations.
    """
)

st.subheader("2. The Reference Score")
st.write(
    """
    A single, simple score is more useful for comparison than a dozen different timings. The **Reference Score** is a weighted average of the most critical performance metrics.
    
    The formula is:
    `Score = ( (1 / CPU_Time) * CPU_Weight ) + ( (1 / GPU_Time) * GPU_Weight ) + ( (1 / Memory_Time) * Memory_Weight )`
    
    We use the inverse of the time (1/time) so that faster completion times result in a higher score. The weights (e.g., `CPU_Weight = 0.4`) are chosen to balance the score based on the perceived importance of each component for general-purpose computing. This creates a single, easy-to-understand number where **higher is better**.
    """
)

st.subheader("3. Configuration Profiles")
st.write(
    """
    Not all tests are created equal. To provide fair comparisons, we offer three testing profiles:
    - **Light**: A quick run with smaller datasets, ideal for a basic performance snapshot.
    - **Standard**: The default profile, providing a balanced and comprehensive test suitable for most users.
    - **Heavy**: A demanding run with very large datasets, designed to push high-end systems to their limits.
    
    Each profile has its own leaderboard, ensuring that results are only compared against other results from the same test configuration.
    """
)
