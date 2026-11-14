import streamlit as st
import subprocess
import os
import sys
from datetime import datetime
import zipfile
import io
import shutil
def create_folder_zip(folder_path):
    zip_buffer = io.BytesIO()

    with zipfile.ZipFile(zip_buffer, "w", zipfile.ZIP_DEFLATED) as zip_file:
        for root, dirs, files in os.walk(folder_path):
            for file in files:
                file_path = os.path.join(root, file)

                # Keep relative folder structure
                arcname = os.path.relpath(file_path, folder_path)

                zip_file.write(file_path, arcname=arcname)

    zip_buffer.seek(0)
    return zip_buffer



def clear_output_folders():
    # Clear CSV files
    if os.path.exists(DATA_DIR):
        for file in os.listdir(DATA_DIR):
            file_path = os.path.join(DATA_DIR, file)
            if file_path.lower().endswith(".csv"):
                os.remove(file_path)

    # Clear PDF files
    if os.path.exists(PDF_DIR):
        for file in os.listdir(PDF_DIR):
            file_path = os.path.join(PDF_DIR, file)
            if file_path.lower().endswith(".pdf"):
                os.remove(file_path)

def run_downloader(force_refresh=False):
    args = [sys.executable, "-m", "src.downloader"]

    if force_refresh:
        args.append("--force")

    start_time = datetime.now()

    result = subprocess.run(
        args,
        cwd=PROJECT_ROOT,
        capture_output=True,
        text=True
    )

    end_time = datetime.now()
    duration = (end_time - start_time).seconds

    return result, duration


def show_refresh_result(result, duration):
    """Show success, a re-login prompt, or the error from the downloader."""
    if result.returncode == 0:
        st.success(f"✅ Data refresh completed in {duration} seconds.")
    elif "Session expired" in result.stderr:
        st.warning("⚠️ Session expired. Please click '🔑 Login to Portal' and try again.")
    else:
        st.error("❌ Data refresh failed.")
        st.text(result.stderr)


# ---------- Paths ----------
PROJECT_ROOT = os.path.dirname(os.path.abspath(__file__))
OUTPUT_DIR = os.path.join(PROJECT_ROOT, "output")
PDF_DIR = os.path.join(OUTPUT_DIR, "pdfs")
DATA_DIR = os.path.join(OUTPUT_DIR, "data")
CSV_FILES = ["life_policies.csv", "general_policies.csv", "clients_metadata.csv"]

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

st.write("**CSV Files:**")
st.code("\n".join(os.path.join(DATA_DIR, name) for name in CSV_FILES))

st.divider()

#------------ login button---------------------

if st.button("🔑 Login to Portal"):
    login = subprocess.run(
        [sys.executable, "-m", "src.auth"],
        cwd=PROJECT_ROOT
    )
    if login.returncode == 0:
        st.success("✅ Login completed.")
    else:
        st.error("❌ Login failed. Check the terminal window for details.")

# ---------- Refresh Buttons ----------
col1, col2 = st.columns(2)

with col1:
    # Incremental: keep existing PDFs so the downloader skips them
    # and only fetches policies that are new since the last run.
    if st.button("🔄 Refresh New Policies"):
        result, duration = run_downloader(force_refresh=False)
        show_refresh_result(result, duration)


with col2:
    # Full rebuild: clear everything and re-download every policy.
    if st.button("♻️ Re-Check All Policies"):
        clear_output_folders()
        result, duration = run_downloader(force_refresh=True)
        show_refresh_result(result, duration)

if os.path.exists(OUTPUT_DIR):

    zip_data = create_folder_zip(OUTPUT_DIR)

    timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")

    st.download_button(
        label="📁 Download Complete Output (PDFs + CSVs)",
        data=zip_data,
        file_name=f"policy_output_{timestamp}.zip",
        mime="application/zip"
    )


    
st.divider()

st.caption(
    "Tip: Make sure the CSV files are closed before refreshing data."
)