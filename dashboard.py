import streamlit as st
from benchHUB.parse_benchmark_results import parse_benchmark_results

# Define path to results directory
RESULTS_DIR = "results"

# Parse benchmark results
st.title("Benchmark Comparison Dashboard")
st.write("Parsing results from:", RESULTS_DIR)

df = parse_benchmark_results(RESULTS_DIR)

# Debugging: Display the raw DataFrame
st.write("### Raw Benchmark Data")
st.dataframe(df)