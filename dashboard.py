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
        /* Use Streamlit's theme variables for compatibility with light/dark modes */
        .stApp {
            background-color: var(--background-color);
            color: var(--text-color);
        }
        /* Minimalist card styling */
        .card {
            border: 1px solid var(--secondary-background-color);
            border-radius: 8px;
            padding: 16px;
            margin: 8px 0;
            background-color: var(--secondary-background-color);
            transition: box-shadow 0.3s ease-in-out;
        }
        .card:hover {
            box-shadow: 0 4px 12px rgba(0,0,0,0.1);
        }
        /* Highlight for search result */
        .highlighted-card {
            border: 1px solid var(--primary-color);
            box-shadow: 0 0 8px var(--primary-color);
        }
        /* Podium card styling */
        .podium-card {
            border: 1px solid gold;
        }
        /* Rank styling */
        .rank {
            font-size: 2em;
            font-weight: bold;
            color: var(--primary-color);
            text-align: center;
        }
        .podium-rank {
            font-size: 3em;
            font-weight: bold;
            text-align: center;
        }
        .gold { color: gold; }
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
        /* Section headers */
        h1, h2, h3 {
            color: var(--text-color);
        }
        /* Clean up sidebar */
        .stSidebar {
            border-right: 1px solid var(--secondary-background-color);
        }
    </style>
    """
    st.markdown(css, unsafe_allow_html=True)

# --- Main Application ---
load_css()

# --- Header and Logo ---
col1, col2, col3 = st.columns([2, 6, 2])
with col2:
    # Use PNG with alpha channel for better theme integration
    st.image("benchHUB.png", use_container_width=True)

st.title("Leaderboard")

# --- Leaderboard Section ---
try:
    response = requests.get(f"{API_URL}/api/leaderboard")
    response.raise_for_status()
    leaderboard_data = response.json()

    if not leaderboard_data:
        st.info("The leaderboard is currently empty. Submit your benchmark to get started!")
    else:
        processed_data = []
        for record in leaderboard_data:
            system_info = json.loads(record.get("system_info", "{}"))
            cpu_info = system_info.get("cpu", {})
            mem_info = system_info.get("memory", {})
            
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
                "memory_total": f"{mem_info.get('total_gb', 'N/A')} GB",
                "timestamp": record.get("timestamp", "N/A")
            })
        
        leaderboard_df = pd.DataFrame(processed_data)
        
        st.sidebar.header("Filters")
        profile_order = ["heavy", "standard", "light"]
        present_profiles = leaderboard_df['config_name'].unique()
        available_profiles = [p for p in profile_order if p in present_profiles]
        config_profiles = ["All"] + available_profiles
        selected_config = st.sidebar.selectbox("Configuration", config_profiles)
        uuid_filter = st.sidebar.text_input("Search by UUID")

        def display_podium(rank, data_row):
            medals = {"1": "🥇", "2": "🥈", "3": "🥉"}
            colors = {"1": "gold", "2": "silver", "3": "bronze"}
            rank_str = str(rank)
            
            score_formatted = f"{int(data_row['reference_index']):,}".replace(",", " ")
            
            st.markdown(f'<div class="card podium-card" style="border-color: {colors.get(rank_str, "var(--secondary-background-color)")};">', unsafe_allow_html=True)
            col1, col2, col3 = st.columns([1, 4, 2])

            with col1:
                st.markdown(f'<p class="podium-rank {colors.get(rank_str, "")}">{medals.get(rank_str, rank_str)}</p>', unsafe_allow_html=True)

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

        def display_card(rank, data_row, is_highlighted=False):
            score_formatted = f"{int(data_row['reference_index']):,}".replace(",", " ")
            card_class = "card highlighted-card" if is_highlighted else "card"
            st.markdown(f'<div class="{card_class}">', unsafe_allow_html=True)
            
            col1, col2, col3 = st.columns([1, 4, 2])

            with col1:
                st.markdown(f'<p class="rank">#{rank}</p>', unsafe_allow_html=True)

            with col2:
                st.markdown(f"""
                    <div class="system-info">
                        <b>CPU:</b> {data_row['cpu_model']}<br>
                        <b>GPU:</b> {data_row['gpu_model']}<br>
                        <b>RAM:</b> {data_row['memory_total']}
                    </div>
                    <div class="uuid">UUID: {data_row['uuid'][:8]} | Submitted: {pd.to_datetime(data_row['timestamp']).strftime('%Y-%m-%d %H:%M')}</div>
                """, unsafe_allow_html=True)

            with col3:
                st.markdown(f'<p class="score">{score_formatted}</p>', unsafe_allow_html=True)
                st.markdown('<p class="score-label" style="text-align: right; opacity: 0.7;">Score</p>', unsafe_allow_html=True)

            st.markdown('</div>', unsafe_allow_html=True)

        def display_leaderboard(df):
            podium_df = df.head(3)
            rest_df = df.iloc[3:]

            if not podium_df.empty:
                st.subheader("Top Performers")
                for i, row in podium_df.iterrows():
                    display_podium(rank=i + 1, data_row=row)
            
            if not rest_df.empty:
                st.subheader("All Results")
                with st.expander("Show all other results...", expanded=True):
                    for i, row in rest_df.iterrows():
                        display_card(rank=i + 1, data_row=row)

        if uuid_filter:
            search_result_df = leaderboard_df[leaderboard_df['uuid'].str.startswith(uuid_filter, na=False)]
            if not search_result_df.empty:
                result_row = search_result_df.iloc[0]
                result_config = result_row['config_name']
                st.header(f"Search Result in '{result_config.capitalize()}'")
                config_df = leaderboard_df[leaderboard_df['config_name'] == result_config].sort_values(by='reference_index', ascending=False).reset_index(drop=True)
                result_index = config_df[config_df['uuid'] == result_row['uuid']].index[0]
                
                st.subheader("Matching Result")
                if result_index < 3:
                    display_podium(rank=result_index + 1, data_row=result_row)
                else:
                    display_card(rank=result_index + 1, data_row=result_row, is_highlighted=True)
                
                st.info("The full leaderboard for this configuration is shown below.")
                display_leaderboard(config_df)

            else:
                st.warning("No results found for this UUID.")
        elif selected_config == "All":
            for profile in available_profiles:
                st.header(f"{profile.capitalize()} Configuration")
                profile_df = leaderboard_df[leaderboard_df['config_name'] == profile].sort_values(by='reference_index', ascending=False).reset_index(drop=True)
                display_leaderboard(profile_df)
                st.markdown("---")
        else:
            st.header(f"{selected_config.capitalize()} Configuration")
            display_df = leaderboard_df[leaderboard_df['config_name'] == selected_config].sort_values(by='reference_index', ascending=False).reset_index(drop=True)
            display_leaderboard(display_df)

except requests.exceptions.RequestException as e:
    st.error(f"Could not connect to the leaderboard API. Please ensure it's running. Error: {e}")