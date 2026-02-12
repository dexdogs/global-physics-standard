import streamlit as st
import pandas as pd
import numpy as np
import requests
import yaml
import time

# --- CONFIGURATION ---
st.set_page_config(page_title="dexdogs | VVB PINN OS", layout="wide", page_icon="🛡️")

# !!! UPDATE THIS !!!
GITHUB_USER = "YOUR_USERNAME_HERE" 
REPO_NAME = "global-physics-standard"
BRANCH = "main"

# 17 SECTOR DEFINITIONS (VCM Standard)
SECTORS = {
    "13": "Waste handling and disposal",
    "01": "Energy industries (renewable/non-renewable)",
    "03": "Energy demand",
    "14": "Afforestation and reforestation",
    "15": "Agriculture",
    "07": "Transport",
    # ... (Add others as needed)
}

# --- BACKEND FUNCTIONS ---

def get_github_physics(sector_id):
    """Fetches the live 'Golden Physics' YAML from GitHub."""
    filename = f"sector_{sector_id}_waste.yaml" # For demo, we default to the waste file format
    url = f"https://raw.githubusercontent.com/{GITHUB_USER}/{REPO_NAME}/{BRANCH}/{filename}"
    
    # Add timestamp to bust cache
    try:
        response = requests.get(f"{url}?t={int(time.time())}")
        if response.status_code == 200:
            return yaml.safe_load(response.text)
        else:
            return None
    except:
        return None

def simulate_pdd_extraction(uploaded_file, sector_id):
    """Simulates Snowflake Cortex extracting physics from a PDF."""
    time.sleep(1.5) # UX Delay
    # Returns 'Paperwork' values. 
    # In a real demo, these might differ from the GitHub 'Truth' to cause a conflict.
    return {
        "project_id": "VCS-2491",
        "extracted_k_value": 0.045, # The value written in the PDF
        "extracted_gas_density": 0.717
    }

def generate_site_data(sector_id):
    """Generates dummy IoT data for the demo."""
    dates = pd.date_range(start="2026-02-01", periods=24, freq="H")
    if sector_id == "13":
        # Landfill Gas Data
        df = pd.DataFrame({
            "Timestamp": dates,
            "Well_Pressure_kPa": np.random.normal(90, 2, 24),
            "Flow_Rate_SCFM": np.random.normal(800, 50, 24),
            "Methane_Conc_%": np.random.normal(50, 1, 24)
        })
        # Inject an anomaly at hour 20
        df.loc[20, "Well_Pressure_kPa"] = 40 # Physics violation (too low for flow)
        return df
    else:
        # Generic Data for other sectors
        return pd.DataFrame({"Timestamp": dates, "Sensor_Value": np.random.normal(100, 10, 24)})

# --- UI LAYOUT ---

st.title("🛡️ dexdogs | Universal VVB PINN OS")
st.markdown("### The Forensic Audit Layer for Voluntary Carbon Markets")

# 1. SECTOR SELECTION
st.sidebar.header("1. Audit Scope")
selected_sector_id = st.sidebar.selectbox(
    "Select Sectoral Scope",
    options=list(SECTORS.keys()),
    format_func=lambda x: f"{x} - {SECTORS[x]}"
)
st.sidebar.markdown(f"[View UNFCCC Sector Definitions](https://cdm.unfccc.int/DOE/scopes.html)")

# 2. PDD UPLOAD (The Paperwork)
st.sidebar.header("2. PDD Ingestion")
pdd_file = st.sidebar.file_uploader("Upload Project Design Document (PDF)", type="pdf")

if pdd_file:
    st.sidebar.success(f"PDD '{pdd_file.name}' Queued")

# MAIN DASHBOARD
col_left, col_right = st.columns([1, 2])

with col_left:
    st.subheader("3. PDD Physics Extraction")
    st.caption("Extracting physical claims from the document...")
    
    if pdd_file:
        with st.spinner("Snowflake Cortex Processing..."):
            pdd_data = simulate_pdd_extraction(pdd_file, selected_sector_id)
            
        st.info(f"**Project Claim:** Methane Decay (k) = `{pdd_data['extracted_k_value']}`")
        st.json(pdd_data)
    else:
        st.warning("Waiting for PDD...")

    st.divider()
    
    st.subheader("4. Scientific Oracle (GitHub)")
    st.caption("Syncing with IME-Approved Standards...")
    
    if st.button("🔄 Sync with GitHub Live"):
        github_physics = get_github_physics(selected_sector_id)
        
        if github_physics:
            st.session_state['physics'] = github_physics
            st.success("✅ Synced with GitHub")
            st.write(f"**Standard:** `{github_physics['physics_standards']['methane_decay_k']}`")
            with st.expander("View Raw YAML"):
                st.json(github_physics)
        else:
            st.error(f"❌ File 'sector_{selected_sector_id}_waste.yaml' not found in repo.")

with col_right:
    st.subheader("5. Field Data & PINN Audit")
    
    # 4. DATA IMPORT
    st.markdown("**Import Site Data (IoT Stream/Excel):**")
    data_source = st.radio("Source:", ["Live API Connection", "Manual Upload"], horizontal=True)
    
    # Simulate Data Load
    site_data = generate_site_data(selected_sector_id)
    st.line_chart(site_data.set_index("Timestamp"))
    
    # 5. PINN CHECK
    st.divider()
    if st.button("🚀 Run PINN Forensic Check", type="primary"):
        if 'physics' in st.session_state and pdd_file:
            
            # THE LOGIC
            pdd_k = pdd_data['extracted_k_value']
            std_k = st.session_state['physics']['physics_standards']['methane_decay_k']
            
            st.markdown("### 🔍 Forensic Result")
            
            c1, c2, c3 = st.columns(3)
            c1.metric("Data Completeness", "100%")
            
            # CHECK: Does PDD match Science?
            if pdd_k == std_k:
                c2.metric("Physics Integrity", "MATCH", delta="Verified")
                st.success(f"✅ **PASS:** Project PDD uses the correct decay constant ({pdd_k}).")
            else:
                c2.metric("Physics Integrity", "FAIL", delta="Violation", delta_color="inverse")
                st.error(f"❌ **FAIL:** Project uses k={pdd_k}, but Science requires k={std_k}.")
                st.warning("⚠️ **Action:** Audit flagged. Do not issue credits.")
                
        else:
            st.error("Please Upload PDD and Sync with GitHub first.")
