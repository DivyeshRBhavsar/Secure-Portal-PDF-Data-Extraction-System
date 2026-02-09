"""
downloader.py

Navigates client records, opens each client in a new tab,
generates a PDF report, downloads it, and updates a CSV file.
"""

import os
import csv
from datetime import datetime
from playwright.sync_api import sync_playwright
import re
from src.pdf_extractor import extract_policy_data, append_to_csv1
from src.utils import sanitize_filename

# ---- Configuration ----
SESSION_FILE = "session.json"
POLICY_INQUIRY_URL = "https://advisor.equitable.ca/advisor/en/tools/policy-inquiry/"
POLICY_COLUMN_INDEX = 3
OUTPUT_DIR = "output"
PDF_DIR = os.path.join(OUTPUT_DIR, "pdfs")
DATA_DIR = os.path.join(OUTPUT_DIR, "data")
CSV_FILE = os.path.join(DATA_DIR, "clients_metadata.csv")

os.makedirs(PDF_DIR, exist_ok=True)
os.makedirs(DATA_DIR, exist_ok=True)


def append_to_csv(row: dict):
    file_exists = os.path.isfile(CSV_FILE)
    with open(CSV_FILE, "a", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(
            f,
            fieldnames=["policy_number", "pdf_filename", "downloaded_at"]
        )
        if not file_exists:
            writer.writeheader()
        writer.writerow(row)




def download_pdfs(headless=False):
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=headless, slow_mo=100)
        context = browser.new_context(
            storage_state=SESSION_FILE,
            accept_downloads=True
        )

        page = context.new_page()

        # ---- Go to Policy Inquiry ----
        page.goto(POLICY_INQUIRY_URL, wait_until="domcontentloaded")

        page.wait_for_selector("text=Policy/New Business Inquiry", timeout=30000)

        # Click Policy Inquiry
        page.click("text=Policy/New Business Inquiry")

        print("Frames on page:")
        for f in page.frames:
            print(f.url)



        page.wait_for_load_state("networkidle")

        # Wait for Search button to exist
        search_button = page.locator("button.btn.btn-primary[type='submit']")

        # Wait until Angular enables it
        page.wait_for_function(
            """() => {
                const btn = document.querySelector("button.btn.btn-primary[type='submit']");
                return btn && !btn.disabled;
            }""",
            timeout=30000
        )
                # Click Search
        search_button.click()

        # Wait for results table
        page.wait_for_selector("table tbody tr", timeout=30000)

        rows = page.locator("table tbody tr")
        row_count = rows.count()
        print(f"Found {row_count} records")
       

        page_number = 1
        

        while True:
            print(f"📄 Processing page {page_number}")

            i = 0
            while True:
                rows = page.locator("table tbody tr")
                if i >= rows.count():
                    break

                row = rows.nth(i)
                i += 1

                # ---- Policy number ----
                policy_cell = row.locator("td").nth(POLICY_COLUMN_INDEX)
                policy_link = policy_cell.locator(
                    "a[href*='/policy/en/policy/index/']"
                )

                # Safety check
                if policy_link.count() == 0:
                    print("⚠️ Policy detail link not found, skipping row")
                    continue

                # Extract policy number
                policy_number = policy_link.text_content().strip()
                # ---- Owner name (column index -2 as you found) ----
                owner_cell = row.locator("td").nth(POLICY_COLUMN_INDEX - 2)
                owner_name = owner_cell.inner_text().strip()

                safe_owner_name = (
                    sanitize_filename(owner_name)
                    if owner_name
                    else "UNKNOWN_OWNER"
                )

                # ---- File paths ----
                pdf_filename = f"{policy_number}_{safe_owner_name}.pdf"
                pdf_path = os.path.join(PDF_DIR, pdf_filename)

                # ---- Skip existing PDFs ----
                if os.path.exists(pdf_path):
                    print(f"Skipping existing file: {pdf_filename}")
                    continue

                print(f"Processing policy {policy_number} ({owner_name})")

        # 👉 continue with:
        # - click policy
        # - generate report
        # - download PDF
        # - extract PDF data

                # ---- Click policy link (opens new tab) ----
                with context.expect_page() as page_info:
                    policy_link.click()

                detail_page = page_info.value
                detail_page.wait_for_load_state("domcontentloaded")
                detail_page.wait_for_load_state("networkidle")

                            # ---- Generate Report (main page) ----
                generate_report = detail_page.locator("#GenerateReport")

                if generate_report.count() == 0:
                    print(
                        f"⚠️ Report not available for policy {policy_number}. Skipping."
                    )
                    detail_page.close()
                    continue

                detail_page.wait_for_selector("#GenerateReport", timeout=30000)

                generate_report_link = detail_page.locator("#GenerateReport")
                generate_report_link.scroll_into_view_if_needed()
                generate_report_link.click()

                # ---- Print dialog iframe ----
                # ---- Wait for Generate Report dialog ----
                done_button = detail_page.locator("#print-done")

                done_button.wait_for(state="visible", timeout=30000)

                # Scroll just in case
                done_button.scroll_into_view_if_needed()

                # ---- Click Done and capture download ----
                with detail_page.expect_download(timeout=60000) as download_info:
                    done_button.click()

                download = download_info.value
                download.save_as(pdf_path)

                data = extract_policy_data(pdf_path)
                append_to_csv1(data, "output/data/policies.csv")

                # ---- Update CSV ----
                append_to_csv({
                    "policy_number": policy_number,
                    "pdf_filename": pdf_filename,
                    "downloaded_at": datetime.utcnow().isoformat()
                })

                print(f"✅ Saved PDF for {policy_number}")

                # ---- Close detail tab ----
                detail_page.close()
            
            next_page_number = page_number + 1

            page_link = page.locator(
            "li.page-item:not(.active) a.page-link",
            has_text=str(next_page_number)
        )

            if page_link.count() == 0:
                print("✅ No more pages found. Finished.")
                break

            print(f"➡️ Moving to page {next_page_number}")
            page_link.first.click()
            page.wait_for_selector("table tbody tr", timeout=30000)

            page_number += 1  

        browser.close()
        print("✅ All downloads completed")


if __name__ == "__main__":
    download_pdfs(headless=False)