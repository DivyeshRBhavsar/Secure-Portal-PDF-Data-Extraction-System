import streamlit as st
import subprocess
import os

PROJECT_ROOT = os.path.dirname(os.path.abspath(__file__))
PDF_DIR = os.path.join(PROJECT_ROOT, "output", "pdfs")
CSV_FILE = os.path.join(PROJECT_ROOT, "output", "data", "policies.csv")

st.set_page_config(page_title="Policy Data Refresh", layout="centered")

st.title("📄 Policy Data Refresh System")

st.markdown("Click the button below to refresh policy PDFs and update the CSV file.")

if st.button("🔄 Refresh Data"):
    with st.spinner("Running data refresh..."):
        subprocess.run(
            ["python", "src/downloader.py"],
            cwd=PROJECT_ROOT
        )
    st.success("✅ Data refreshed successfully!")

st.markdown("---")
st.subheader("📁 Output Locations")

st.write("**PDF Folder:**")
st.code(PDF_DIR)

st.write("**CSV File:**")
st.code(CSV_FILE)