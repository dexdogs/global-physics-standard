import streamlit as st
import pandas as pd
import requests
import yaml
import time

# --- CONFIG ---
st.set_page_config(page_title="dexdogs | VVB PINN OS", layout="wide")

# REPLACE with your GitHub details
GITHUB_USER = "YOUR_USERNAME"
REPO = "global-physics-standard"
FILE_PATH = "sector_13_landfill.yaml"
RAW_URL = f"https://raw.githubusercontent.com/{GITHUB_USER}/{REPO}/main/{FILE_PATH}"

# --- FUNCTIONS ---
def get_physics_from_github():
    try:
        # Use a timestamp to bypass GitHub's cache for live demo updates
        response = requests.get(f"{RAW_URL}?t={int(time.time())}")
        if response.status_code == 200:
            return yaml.safe_load(response.text)
    except Exception as e:
        st.error(f"GitHub Error: {e}")
    return None

# --- UI ---
st.title("🛡️ VVB Physics-Informed Verification OS")
st.markdown(f"**Scientific Oracle:** `{REPO}/{FILE_PATH}`")

col1, col2 = st.columns([1, 2])

with col1:
    st.header("1. Sync Science")
    if st.button("🔄 Sync with GitHub"):
        data = get_physics_from_github()
        if data:
            st.session_state['physics'] = data
            st.success("Synced!")
            st.json(data)

with col2:
    st.header("2. Forensic Audit")
    if 'physics' in st.session_state:
        # Simulate a PDD extraction
        pdd_k = 0.042 
        st.info(f"📄 **PDD Scanned:** Project claims methane decay (k) of **{pdd_k}**")
        
        if st.button("🚀 Run PINN Physics Check"):
            with st.spinner("Validating against laws of nature..."):
                time.sleep(1)
                standard_k = st.session_state['physics']['physics_constraints']['methane_generation']['decay_k_value']
                
                if pdd_k == standard_k:
                    st.success("✅ Physics Match")
                else:
                    st.error("❌ Physics Violation")
                    st.warning(f"Project k ({pdd_k}) does not match Scientific Standard ({standard_k})")
