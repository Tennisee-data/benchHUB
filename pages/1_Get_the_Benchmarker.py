import streamlit as st

st.header("📥 Get the Benchmarker")

st.write("""
Ready to benchmark your system? Download the latest version of benchHUB and contribute your results to our anonymous leaderboard.
""")

# Download section
col1, col2 = st.columns([2, 1])

with col1:
    st.subheader("🍎 macOS Download")
    st.write("**Latest Version: v1.0.0** - Includes scoring fixes and security improvements")
    
    # Direct download button
    st.markdown('''
    <a href="https://github.com/Tennisee-data/benchHUB/releases/download/v1.0.0/benchHUB-macos.zip" target="_blank">
        <button style="
            width: 100%; 
            padding: 15px; 
            background-color: #1E90FF; 
            color: white; 
            border: none; 
            border-radius: 8px; 
            font-size: 1.2em;
            font-weight: bold;
            cursor: pointer;
            margin: 10px 0;
        ">
            📥 Download for macOS
        </button>
    </a>
    ''', unsafe_allow_html=True)
    
    st.write("**Requirements:** macOS 10.15+ (optimised for Apple Silicon)")

with col2:
    st.subheader("🔗 Additional Resources")
    
    # Source code link
    st.markdown('''
    <a href="https://github.com/Tennisee-data/benchHUB" target="_blank">
        <button style="
            width: 100%; 
            padding: 10px; 
            background-color: #28a745; 
            color: white; 
            border: none; 
            border-radius: 5px; 
            font-size: 1em;
            margin: 5px 0;
        ">
            📄 View Source Code
        </button>
    </a>
    ''', unsafe_allow_html=True)
    
    # Release notes link
    st.markdown('''
    <a href="https://github.com/Tennisee-data/benchHUB/releases" target="_blank">
        <button style="
            width: 100%; 
            padding: 10px; 
            background-color: #6c757d; 
            color: white; 
            border: none; 
            border-radius: 5px; 
            font-size: 1em;
            margin: 5px 0;
        ">
            📋 Release Notes
        </button>
    </a>
    ''', unsafe_allow_html=True)

# Installation instructions
st.subheader("🛠️ Quick Setup")
st.write("""
1. **Download** the zip file above
2. **Unzip** and read the included README.txt
3. **Run setup.sh** to bypass macOS's Gatekeeper (one-time only)
4. **Launch** by double-clicking start-benchHUB

**Need help?** The README.txt includes detailed setup instructions with two methods for navigating to the folder in a new terminal window.
""")

# Trust indicators
st.subheader("🛡️ Open Source & Secure")
st.write("""
- **100% Open Source**: All code is publicly available on GitHub
- **No data collection**: Only anonymous benchmark results are shared (if you choose)
- **Security verified**: Server-side validation prevents manipulation
- **Community driven**: Contributions welcome!
""")

# Alternative link for those who prefer the full website
st.divider()
st.write("**Prefer the full download page?**")
st.markdown('<a href="https://tennisee-data.github.io/benchHUB_web/" target="_blank">Visit benchHUB on GitHub →</a>', unsafe_allow_html=True)
