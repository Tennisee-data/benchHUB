import streamlit as st

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
    - **CPU (Prime Calculation)**: A pure computational task that calculates a large number of prime numbers. It's designed to be CPU-bound with low memory usage, testing single-core processing power.
    - **CPU (Parallel Processing)**: Tests the CPU's ability to handle multiple tasks simultaneously, crucial for modern applications.
    - **GPU (Tensor Operations)**: Stresses the GPU with matrix multiplications, a fundamental operation in machine learning and 3D graphics.
    - **Memory (Bandwidth)**: Measures the speed of data movement in system memory by timing large array copy operations, a more practical metric than simple allocation.
    - **Disk (Read/Write)**: Tests the sequential read and write speed of your primary storage drive using a moderately sized file.
    - **Machine Learning (Training)**: Simulates a real-world ML model training task (Random Forest) to evaluate a combination of CPU, GPU, and memory performance.
    - **Plotting (Complex Visuals)**: Measures the time to generate and render complex data visualizations.
    """
)

st.subheader("2. The Reference Score")
st.write(
    """
    A single, simple score is more useful for comparison than a dozen different timings. The **Reference Score** is a weighted average of the most critical performance metrics.
    
    The formula is:
    `Score = ( (1 / CPU_Time) * CPU_Weight ) + ( (1 / GPU_Time) * GPU_Weight ) + ( (1 / Memory_Time) * Memory_Weight )`
    
    We use the inverse of the time (1/time) so that faster completion times result in a higher score. The weights are chosen to balance the score based on the perceived importance of each component for general-purpose computing. This creates a single, easy-to-understand number where **higher is better**.
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
