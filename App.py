import streamlit as st
import subprocess
import os
import sys
from datetime import datetime


def run_downloader(force_refresh=False):
    args = [sys.executable, "-m", "src.downloader"]

    if force_refresh:
        args.append("--force")

    result = subprocess.run(
        args,
        cwd=PROJECT_ROOT,
        capture_output=True,
        text=True
    )


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

#------------ login button---------------------

if st.button("🔑 Login to Portal"):
    subprocess.run(
        [sys.executable, "-m", "src.auth"],
        cwd=PROJECT_ROOT
    )
    st.success("✅ Login completed.")

# ---------- Refresh Button ----------
col1, col2 = st.columns(2)

with col1:
    if st.button("🔄 Refresh New Policies"):
        run_downloader(force_refresh=False)

with col2:
    if st.button("♻️ Re-Check All Policies"):
        run_downloader(force_refresh=True)

    start_time = datetime.now()

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
        if "Session expired" in result.stderr:
            st.warning("⚠️ Session expired. Please click 'Re-Login to Portal'.")
        else:
            st.error("❌ Data refresh failed.")
            st.text(result.stderr)

st.divider()

st.caption(
    "Tip: Make sure the CSV file is closed before refreshing data."
)