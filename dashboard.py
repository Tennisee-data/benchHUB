import logging
import streamlit as st
import pandas as pd
import requests
import json
import os

# Configure logging
logging.getLogger('matplotlib').setLevel(logging.ERROR)

# --- Page Configuration ---
st.set_page_config(layout="wide", page_title="benchHUB Leaderboard")

# --- Environment and Constants ---
API_URL = os.environ.get("API_URL", "https://benchhub-api.onrender.com")

# --- Custom CSS for Styling ---
def load_css():
    css = """
    <style>
        /* Reduce top padding to move content up */
        .block-container {
            padding-top: 2rem;
        }
        
        /* Main container for each leaderboard entry */
        .list-item {
            border-bottom-style: solid;
            border-bottom-width: 1px;
            border-bottom-color: var(--secondary-background-color);
            padding: 1.2rem 0.5rem;
            transition: background-color 0.3s ease-in-out;
        }
        .list-item:hover {
            background-color: var(--secondary-background-color);
        }

        /* Podium Separator Styles */
        .podium-1 { border-bottom-width: 3px; border-bottom-color: #FFD700; } /* Gold */
        .podium-2 { border-bottom-width: 2px; border-bottom-color: #C0C0C0; } /* Silver */
        .podium-3 { border-bottom-width: 2px; border-bottom-color: #CD7F32; } /* Bronze */

        /* Highlight for search result */
        .highlighted-item {
            background-color: #273346; /* A neutral blue highlight */
        }

        /* Rank styling */
        .rank {
            font-size: 2em;
            font-weight: bold;
            color: var(--text-color);
            opacity: 0.8;
            text-align: center;
        }
        .podium-rank {
            font-size: 3em;
            font-weight: bold;
            text-align: center;
        }
        .gold { color: #FFD700; }
        .silver { color: #C0C0C0; }
        .bronze { color: #CD7F32; }

        /* Score styling */
        .score {
            font-size: 1.8em;
            font-weight: bold;
            color: var(--text-color);
            text-align: right;
        }
        /* System info styling */
        .system-info {
            font-size: 1em;
            color: var(--text-color);
            line-height: 1.6;
        }
        /* UUID styling */
        .uuid {
            font-size: 0.8em;
            color: var(--text-color);
            opacity: 0.7;
            font-family: monospace;
        }
        
        /* Category Header with Background Mask */
        .category-header {
            background-color: var(--secondary-background-color);
            padding: 0.5rem 1rem;
            border-radius: 8px;
            margin-top: 2rem;
            margin-bottom: 1rem;
        }
        .category-header h2 {
            margin: 0;
            padding: 0;
        }

    </style>
    """
    st.markdown(css, unsafe_allow_html=True)

# --- Main Application ---
load_css()

# --- Header and Logo ---
col1, col2, col3 = st.columns([3, 4, 3])
with col2:
    st.image("benchHUB.png", use_container_width=True)
    st.markdown('<h3 style="text-align: center;">Benchmark your hardware for machine learning, data science and AI. See how your hardware rates with others. Download the benchmarker and get an index score.</h3>', unsafe_allow_html=True)

st.title("Leaderboard")

# --- Leaderboard Section ---
try:
    response = requests.get(f"{API_URL}/api/leaderboard")
    response.raise_for_status()
    leaderboard_data = response.json()

    if not leaderboard_data:
        st.info("The leaderboard is currently empty. Submit your benchmark to get started!")
    else:
        # Process data
        processed_data = []
        for record in leaderboard_data:
            system_info = json.loads(record.get("system_info", "{}"))
            cpu_info = system_info.get("cpu", {})
            mem_info = system_info.get("memory", {})
            gpu_model = "N/A"
            if "gpus" in system_info and isinstance(system_info["gpus"], list) and system_info["gpus"]:
                gpu_model = ", ".join([gpu.get("name", "N/A") for gpu in system_info["gpus"]])
            elif "torch_gpus" in system_info and isinstance(system_info["torch_gpus"], dict):
                gpu_model = ", ".join(system_info["torch_gpus"].get("device_names", ["N/A"]))

            processed_data.append({
                "id": record["id"], "reference_index": record["reference_index"],
                "config_name": record.get("config_name", "standard"), "uuid": record.get("uuid", "N/A"),
                "cpu_model": cpu_info.get("model", "Unknown CPU"), "gpu_model": gpu_model,
                "memory_total": f"{mem_info.get('total_gb', 'N/A')} GB", "timestamp": record.get("timestamp", "N/A")
            })
        
        leaderboard_df = pd.DataFrame(processed_data)
        
        # --- Sidebar ---
        st.sidebar.header("Filters")
        profile_order = ["heavy", "standard", "light"]
        present_profiles = leaderboard_df['config_name'].unique()
        available_profiles = [p for p in profile_order if p in present_profiles]
        config_profiles = ["All"] + available_profiles
        selected_config = st.sidebar.selectbox("Configuration", config_profiles)
        uuid_filter = st.sidebar.text_input("Search by UUID")

        # --- Display Functions ---
        def display_entry(rank, data_row, is_highlighted=False):
            medals = {"1": "🥇", "2": "🥈", "3": "🥉"}
            podium_classes = {1: "podium-1", 2: "podium-2", 3: "podium-3"}
            color_classes = {1: "gold", 2: "silver", 3: "bronze"}
            
            item_class = "list-item " + podium_classes.get(rank, "")
            if is_highlighted:
                item_class += " highlighted-item"

            score_formatted = f"{int(data_row['reference_index']):,}".replace(",", " ")
            
            st.markdown(f'<div class="{item_class}">', unsafe_allow_html=True)
            col1, col2, col3 = st.columns([1, 4, 2])

            with col1:
                if rank <= 3:
                    st.markdown(f'<p class="podium-rank {color_classes.get(rank, "")}">{medals.get(str(rank), rank)}</p>', unsafe_allow_html=True)
                else:
                    st.markdown(f'<p class="rank">#{rank}</p>', unsafe_allow_html=True)

            with col2:
                st.markdown(f"""
                    <div class="system-info">
                        <b>CPU:</b> {data_row['cpu_model']}<br>
                        <b>GPU:</b> {data_row['gpu_model']}<br>
                        <b>RAM:</b> {data_row['memory_total']}
                    </div>
                    <div class="uuid">UUID: {data_row['uuid'][:8]} | {pd.to_datetime(data_row['timestamp']).strftime('%Y-%m-%d')}</div>
                """, unsafe_allow_html=True)

            with col3:
                st.markdown(f'<p class="score">{score_formatted}</p>', unsafe_allow_html=True)
                st.markdown('<p class="score-label" style="text-align: right; opacity: 0.7;">Score</p>', unsafe_allow_html=True)

            st.markdown('</div>', unsafe_allow_html=True)

        def display_leaderboard(df):
            for i, row in df.iterrows():
                display_entry(rank=i + 1, data_row=row)

        # --- Main Display Logic ---
        if uuid_filter:
            search_result_df = leaderboard_df[leaderboard_df['uuid'].str.startswith(uuid_filter, na=False)]
            if not search_result_df.empty:
                result_row = search_result_df.iloc[0]
                result_config = result_row['config_name']
                
                st.markdown(f'<div class="category-header"><h2>Search Result in \'{result_config.capitalize()}\'</h2></div>', unsafe_allow_html=True)
                config_df = leaderboard_df[leaderboard_df['config_name'] == result_config].sort_values(by='reference_index', ascending=False).reset_index(drop=True)
                result_index = config_df[config_df['uuid'] == result_row['uuid']].index[0]
                
                display_entry(rank=result_index + 1, data_row=result_row, is_highlighted=True)
                
                st.info("The full leaderboard for this configuration is shown below.")
                display_leaderboard(config_df)
            else:
                st.warning("No results found for this UUID.")
        
        elif selected_config == "All":
            for i, profile in enumerate(available_profiles):
                st.markdown(f'<div class="category-header"><h2>{profile.capitalize()} Configuration</h2></div>', unsafe_allow_html=True)
                profile_df = leaderboard_df[leaderboard_df['config_name'] == profile].sort_values(by='reference_index', ascending=False).reset_index(drop=True)
                display_leaderboard(profile_df)
                if i < len(available_profiles) - 1:
                    st.divider()
        else:
            st.markdown(f'<div class="category-header"><h2>{selected_config.capitalize()} Configuration</h2></div>', unsafe_allow_html=True)
            display_df = leaderboard_df[leaderboard_df['config_name'] == selected_config].sort_values(by='reference_index', ascending=False).reset_index(drop=True)
            display_leaderboard(display_df)

except requests.exceptions.RequestException as e:
    st.error(f"Could not connect to the leaderboard API. Please ensure it's running. Error: {e}")
