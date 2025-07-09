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

st.title("🏆 benchHUB Online Leaderboard")

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
        # Sort profiles to have a consistent order
        available_profiles = sorted(leaderboard_df['config_name'].unique())
        config_profiles = ["All"] + available_profiles
        selected_config = st.sidebar.selectbox("Filter by Configuration", config_profiles)

        uuid_filter = st.sidebar.text_input("Filter by UUID (or partial UUID)")

        # --- Display Logic ---
        
        # Function to display a single result card
        def display_card(rank, data_row):
            score_formatted = f"{int(data_row['reference_index']):,}".replace(",", " ")
            st.markdown('<div class="card">', unsafe_allow_html=True)
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
            display_df = leaderboard_df[leaderboard_df['uuid'].str.startswith(uuid_filter, na=False)]
            st.subheader(f"Search Results for '{uuid_filter}'")
            if display_df.empty:
                st.warning("No results found for this UUID.")
            else:
                for i, row in display_df.iterrows():
                    display_card(rank="-", data_row=row) # No rank for search results
        
        # Display by configuration
        elif selected_config == "All":
            for profile in available_profiles:
                st.subheader(f"{profile.capitalize()} Configuration")
                profile_df = leaderboard_df[leaderboard_df['config_name'] == profile].sort_values(by='reference_index', ascending=False)
                for i, row in enumerate(profile_df.iterrows()):
                    display_card(rank=i + 1, data_row=row[1])
                st.markdown("---")
        
        else: # A specific configuration is selected
            st.subheader(f"{selected_config.capitalize()} Configuration")
            display_df = leaderboard_df[leaderboard_df['config_name'] == selected_config].sort_values(by='reference_index', ascending=False)
            for i, row in enumerate(display_df.iterrows()):
                display_card(rank=i + 1, data_row=row[1])


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