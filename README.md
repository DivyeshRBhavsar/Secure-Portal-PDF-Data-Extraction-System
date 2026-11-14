# 🔐 Secure Portal PDF Data Extraction System

[![CI - Secure PDF Data Extraction](https://github.com/DivyeshRBhavsar/Secure-Portal-PDF-Data-Extraction-System/actions/workflows/CI.yml/badge.svg)](https://github.com/DivyeshRBhavsar/Secure-Portal-PDF-Data-Extraction-System/actions/workflows/CI.yml)

This tool pulls insurance policy reports from a secure, OTP-protected web portal, extracts their data, and saves it as clean, de-duplicated CSV files. Everything runs from a **one-click Streamlit app**.

> ⚠️ All PDFs and CSVs in this repository are **synthetic sample data**. No real client data is included.

---

## 📌 Problem statement

The client needs a dashboard to analyse data from policy PDF reports, but those reports live inside a secure portal. Today every report is **downloaded and transcribed by hand**, which is slow, error-prone and impossible to keep up to date.

This project replaces that manual work with an automated pipeline. It:
- **Logs in:** signs in to the portal securely, including two-factor (OTP) login.
- **Downloads:** saves every policy report as a PDF.
- **Extracts:** pulls structured fields out of each PDF.
- **Stores:** writes the data to CSV, one row per policy, with no duplicates, ready for a BI dashboard.

---

## ✨ Features

- **One-click refresh:** a Streamlit interface lets non-technical users run the whole pipeline.
- **Secure, reusable login:**
  - The user signs in once in a real browser, including the OTP.
  - Playwright saves that signed-in session and reuses it for later runs.
  - No passwords are stored in code.
- **Automated portal navigation:**
  - Searches all policies and pages through the results table.
  - Opens each policy and generates its report, then captures the PDF download.
- **Smart PDF parsing** with `pdfplumber`:
  - Detects whether a report is a **Life** or a **General** (investment) policy.
  - Handles several layouts for the same field, such as an inline `Sex Date of Birth` line versus separate lines, or labelled deposits versus a four-value row.
  - Validates the required Life fields and logs the failures.
- **No duplicates:** each policy number gets one row. Re-running the pipeline updates rows instead of adding duplicates.
- **Incremental or full refresh:**
  - **New policies only:** skips policies whose PDF already exists.
  - **Re-check all:** forces every policy to be downloaded and parsed again.
- **Download everything:** the app offers all PDFs and CSVs as a single timestamped ZIP.
- **Tested in CI:** pytest runs on every push through GitHub Actions, against generated sample PDFs.

---

## 🧭 How it works

```
 ┌──────────────┐   manual login + OTP    ┌──────────────┐
 │  Streamlit   │ ──────────────────────▶ │   auth.py    │ ──▶ session.json
 │   App.py     │                         └──────────────┘    (saved session)
 │              │   Refresh / Re-check    ┌──────────────┐
 │              │ ──────────────────────▶ │ downloader.py│
 └──────────────┘                         │  Playwright  │
        ▲                                 │  • search    │
        │ ZIP download                    │  • paginate  │
        │                                 │  • report→PDF│
        │                                 └──────┬───────┘
        │                                        ▼
        │                                 ┌──────────────┐
        │                                 │pdf_extractor │  Life vs General
        │                                 │ (pdfplumber) │  field parsing
        │                                 └──────┬───────┘
        │                                        ▼
        │                                 ┌──────────────┐
        └──────────────────────────────── │ csv_writer   │  update or insert
                                          │ by policy no.│
                                          └──────────────┘
```

### Extracted fields

| Life policies (`life_policies.csv`) | General policies (`general_policies.csv`) |
|---|---|
| Policy number, product name | Policy number, contract type (e.g. RRSP, FHSA) |
| Face amount, death benefit, accidental death benefit | Total deposits, total withdrawals, net deposits |
| Tax indicator, coverage status | Market value, maturity date |
| Effective date, premium end date, paid-to date | Owner name, address, phone, email |
| Premium mode, amount, minimum premium, next payment date, billing method | Sex, date of birth |
| Owner name, insured name, date of birth, sex | |

`clients_metadata.csv` keeps a log of each download, with the policy number, PDF filename and a UTC timestamp.

---

## 📁 Project structure

```
├── App.py                     # Streamlit UI: login, refresh, re-check, ZIP download
├── src/
│   ├── auth.py                # Opens the portal, waits for manual login + OTP, saves the session
│   ├── downloader.py          # Playwright navigation, pagination, PDF download
│   ├── pdf_extractor.py       # Life / General field extraction (pdfplumber + regex)
│   ├── csv_writer.py          # Updates or inserts CSV rows by policy number
│   └── utils.py               # Filename cleaning
├── tests/
│   ├── fixtures/              # reportlab scripts that generate the sample PDFs
│   ├── test_pdf_extractor.py
│   └── test_utils.py
├── sample_pdfs/               # Synthetic Life and General policy PDFs used in tests
├── sample_output/             # Example CSV output (synthetic data)
├── .github/workflows/CI.yml   # GitHub Actions: runs pytest on every push / PR
├── start_app.bat              # One-click Windows launcher
├── .env.example               # Template for the portal URLs
├── Dockerfile
└── requirements.txt
```

---

## 🚀 Getting started

### 1. Configure the portal
Copy `.env.example` to `.env` and fill in your portal's two URLs. `.env` is git-ignored, so it stays on your machine.
```
PORTAL_URL=https://<your-portal-login-url>
POLICY_INQUIRY_URL=https://<your-portal-policy-inquiry-url>
```

### 2. Run the app

**Windows (one click):** double-click `start_app.bat`. It:
- creates a virtual environment
- installs the requirements
- installs Playwright's Chromium browser
- launches the app

**Manual setup:**
```bash
python -m venv .venv
source .venv/bin/activate          # Windows: .venv\Scripts\activate
pip install -r requirements.txt
playwright install chromium
streamlit run App.py
```

### 3. Use it
1. Click **🔑 Login to Portal**. A browser window opens. Sign in with your username, password and OTP, then press **Enter** in the terminal to save the session.
2. Click **🔄 Refresh New Policies** for an incremental update, or **♻️ Re-Check All Policies** for a full rebuild. If the saved session has expired, the app asks you to log in again.
3. Click **📁 Download Complete Output** to get every PDF and CSV as one ZIP.

Results are saved to `output/pdfs/` and `output/data/`. Both folders are git-ignored.

---

## 🧪 Testing

```bash
pytest -v
```

The tests build mock Life and General policy PDFs with `reportlab`, and check that every schema field is extracted and the key values are filled in. The same suite runs in **GitHub Actions** on every push and pull request to `main`.

---

## 🔒 Security and privacy

- **No credentials in the code.** The user enters the password and OTP in the browser, and only the portal URLs are read from `.env`.
- **Secrets stay out of git.** `session.json`, `.env` and all `output/` files are git-ignored.
- **Personal data stays local.** The extracted CSVs contain personal information (names, addresses, dates of birth), so they are written only to your machine and never committed.

## ⚠️ Limitations

- **Login needs a person.** Because of the OTP, a human must complete each login, so a fully unattended schedule isn't possible.
- **Depends on the portal's layout.** Navigation relies on its page structure and CSS selectors, so a portal redesign means updating `downloader.py`.
- **Depends on the PDF templates.** PDF parsing is rule-based and tied to the current report layouts.
- **Docker needs extra setup.** The login step opens a visible browser, so the Docker image needs a display for it to work.

## 🛠️ Tech stack

Python · Playwright · pdfplumber · Streamlit · pandas · pytest · reportlab · GitHub Actions · Docker

---

## 👤 Author

**Divyesh Bhavsar**
GitHub: [@DivyeshRBhavsar](https://github.com/DivyeshRBhavsar)
