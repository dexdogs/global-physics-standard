import streamlit as st
import pandas as pd
import numpy as np
import requests
import yaml
import time

# --- CONFIGURATION ---
st.set_page_config(page_title="Physics-based Verification Demo // dexdogs", layout="wide")

# !!! CRITICAL: UPDATE THESE TO MATCH YOUR GITHUB REPO !!!
GITHUB_USER = "dexdogs" 
REPO_NAME = "global-physics-standard"
BRANCH = "main"

# 17 SECTOR DEFINITIONS (VCM Standard)
SECTORS = {
    "13": "Waste handling and disposal",
    "01": "Energy industries",
    "03": "Energy demand",
    "14": "Afforestation/Reforestation",
    "15": "Agriculture",
    "07": "Transport"
}

# --- BACKEND FUNCTIONS ---

def get_github_physics(sector_id):
    """Fetches the live 'Golden Physics' YAML from GitHub with Debug Info."""
    filename = f"sector_{sector_id}_waste.yaml"
    url = f"https://raw.githubusercontent.com/{GITHUB_USER}/{REPO_NAME}/{BRANCH}/{filename}"
    
    # DEBUG DRAWER IN SIDEBAR
    st.sidebar.markdown("---")
    st.sidebar.subheader("Debug Terminal")
    st.sidebar.caption(f"Target URL: {url}")
    
    try:
        # Use a timestamp to prevent GitHub caching during live edits
        response = requests.get(f"{url}?t={int(time.time())}")
        
        if response.status_code == 200:
            st.sidebar.success("URL Status: 200 (Found)")
            return yaml.safe_load(response.text)
        elif response.status_code == 404:
            st.sidebar.error("URL Status: 404 (File Not Found)")
            st.sidebar.info("Check: 1. Username 2. Repo Name 3. Branch 4. Filename case sensitivity")
            return None
        else:
            st.sidebar.error(f"URL Status: {response.status_code}")
            return None
    except Exception as e:
        st.sidebar.error(f"Connection Error: {e}")
        return None

def simulate_pdd_extraction(uploaded_file, sector_id):
    """Simulates Snowflake Cortex extracting physics from a PDD PDF."""
    time.sleep(1.5)
    # The PDD value we want to compare (Lumbini/Vinca often around 0.05)
    return {
        "project_id": "VCS-2491",
        "extracted_k_value": 0.05, 
        "methodology": "ACM0001",
        "gas_density": 0.717
    }

def generate_site_data(sector_id):
    """Generates synthetic IoT data for the PINN graph."""
    dates = pd.date_range(start="2026-02-01", periods=24, freq="H")
    if sector_id == "13":
        df = pd.DataFrame({
            "Timestamp": dates,
            "Well_Pressure_kPa": np.random.normal(90, 2, 24),
            "Flow_Rate_SCFM": np.random.normal(800, 50, 24)
        })
        # Inject an anomaly at the end to show 'Forensic Alert'
        df.loc[20:23, "Well_Pressure_kPa"] = 35 
        return df
    return pd.DataFrame({"Timestamp": dates, "Sensor": np.random.normal(100, 5, 24)})

# --- UI LAYOUT ---

st.title("Physics-based Verification Demo // dexdogs")
st.markdown("### Physics-nerd AI assistant for the VVBs/auditors of the world")

# 1. SIDEBAR SETUP
st.sidebar.header("1. Audit Scope")
selected_sector_id = st.sidebar.selectbox(
    "Select Sectoral Scope",
    options=list(SECTORS.keys()),
    format_func=lambda x: f"{x} - {SECTORS[x]}"
)
st.sidebar.markdown(f"[View VCM Sector Definitions](https://cdm.unfccc.int/DOE/scopes.html)")

st.sidebar.header("2. PDD Ingestion")
pdd_file = st.sidebar.file_uploader("Upload Project Design Document (PDF)", type="pdf")

# MAIN APP COLUMNS
col_left, col_right = st.columns([1, 2])

with col_left:
    st.subheader("3. PDD Science Extraction")
    if pdd_file:
        with st.spinner("Snowflake Cortex analyzing PDF..."):
            pdd_data = simulate_pdd_extraction(pdd_file, selected_sector_id)
        st.info(f"📄 **PDD Scanned:** '{pdd_file.name}'")
        st.markdown(f"**Extracted k-value:** `{pdd_data['extracted_k_value']}`")
        with st.expander("View Full Extraction JSON"):
            st.json(pdd_data)
    else:
        st.warning("Please upload a PDD to begin.")

    st.divider()
    
    st.subheader("4. Scientific Oracle (GitHub)")
    if st.button("🔄 Sync with GitHub Live", type="secondary"):
        github_physics = get_github_physics(selected_sector_id)
        if github_physics:
            st.session_state['physics'] = github_physics
            st.success("✅ Science Standard Synced")
            st.markdown(f"**Required k-value:** `{github_physics['physics_standards']['methane_decay_k']}`")
        else:
            st.error("Check Debug Terminal in Sidebar for details.")

with col_right:
    st.subheader("5. Field Data & PINN Audit")
    
    # Site Data Chart
    site_data = generate_site_data(selected_sector_id)
    st.line_chart(site_data.set_index("Timestamp"))
    st.caption("Live IoT Stream: Well Pressure vs Time")
    
    # THE PINN EXECUTION
    st.divider()
    if st.button("🚀 Run Forensic PINN Audit", type="primary"):
        if 'physics' in st.session_state and pdd_file:
            
            pdd_k = pdd_data['extracted_k_value']
            std_k = st.session_state['physics']['physics_standards']['methane_decay_k']
            
            st.markdown("### 🔍 Verification Results")
            
            # THE DASHBOARD
            res1, res2, res3 = st.columns(3)
            res1.metric("Methodology", pdd_data['methodology'])
            
            # COMPARISON LOGIC
            if abs(pdd_k - std_k) < 0.001:
                res2.metric("Physics Integrity", "MATCH", delta="Verified")
                st.success(f"✅ **PASS:** Project k-value ({pdd_k}) is physically accurate.")
            else:
                res2.metric("Physics Integrity", "FAIL", delta="Violation", delta_color="inverse")
                st.error(f"❌ **FAIL:** Project uses k={pdd_k}. Scientific Oracle requires k={std_k}.")
                st.warning("⚠️ **VVB ALERT:** Liability detected. Do not issue credits.")
            
            res3.metric("Audit Latency", "1.5s", delta="Manual: 45 Days", delta_color="inverse")
                
        else:
            st.error("Missing Data: Please ensure PDD is uploaded and GitHub is Synced.")
