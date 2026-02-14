import streamlit as st
import subprocess
import os
import sys
from datetime import datetime

# ---------- Paths ----------
PROJECT_ROOT = os.path.dirname(os.path.abspath(__file__))
PDF_DIR = os.path.join(PROJECT_ROOT, "output", "pdfs")
CSV_FILE = os.path.join(PROJECT_ROOT, "output", "data", "policies.csv")

# ---------- Page Config ----------
st.set_page_config(
    page_title="Policy Data Refresh",
    layout="centered"
)

st.title("📄 Policy Data Refresh System")

st.markdown(
    """
This tool allows you to refresh policy data with **one click**.

- PDFs will be downloaded automatically
- The CSV file will be updated with the latest data
"""
)

st.divider()

# ---------- Show Output Locations ----------
st.subheader("📁 Output Locations")

st.write("**PDF Folder:**")
st.code(PDF_DIR)

st.write("**CSV File:**")
st.code(CSV_FILE)

st.divider()

# ---------- Refresh Button ----------
if st.button("🔄 Refresh Data"):
    st.info("Running data refresh. Please wait...")

    try:
        start_time = datetime.now()

        # Run downloader as a module (IMPORTANT)
        result = subprocess.run(
            [sys.executable, "-m", "src.downloader"],
            cwd=PROJECT_ROOT,
            capture_output=True,
            text=True
        )

        end_time = datetime.now()
        duration = (end_time - start_time).seconds

        if result.returncode == 0:
            st.success(f"✅ Data refresh completed in {duration} seconds.")
        else:
            st.error("❌ Data refresh failed.")
            st.text(result.stderr)

    except Exception as e:
        st.error("❌ Unexpected error occurred.")
        st.text(str(e))

st.divider()

st.caption(
    "Tip: Make sure the CSV file is closed before refreshing data."
)