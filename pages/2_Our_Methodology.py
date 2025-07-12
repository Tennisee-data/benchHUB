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
    A single, simple score is more useful for comparison than a dozen different timings. The **Reference Score** is a weighted composite of the most critical performance metrics.
    
    **Current Formula (v1.0.1+):**
    ```
    CPU_Score = (1 / CPU_Time) × 0.4
    GPU_Score = (1 / GPU_Time) × 0.4  
    Memory_Score = (1 / Memory_Time) × 0.2
    
    Raw_Score = CPU_Score + GPU_Score + Memory_Score
    Final_Score = min(Raw_Score × 0.5, 999.9)
    ```
    
    **Key Features:**
    - **Inverse timing**: Faster completion = higher score
    - **Weighted components**: CPU (40%), GPU (40%), Memory (20%)
    - **Capped at 999.9**: Ensures scores remain intuitive and comparable
    - **Security validated**: Server-side verification prevents manipulation
    
    This creates a single, easy-to-understand number where **higher is better**, with typical scores ranging from 200-900 depending on hardware and test profile.
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
