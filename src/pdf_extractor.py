import pdfplumber
import re
import pandas as pd
import os


def normalize_lines(text: str) -> list[str]:
    return [line.strip() for line in text.splitlines() if line.strip()]

def get_all_pages_lines(pdf):
    pages_lines = []
    for page in pdf.pages:
        text = page.extract_text() or ""
        pages_lines.append(normalize_lines(text))
    return pages_lines

def find_page_with_keyword(pages_lines, keyword):
    keyword = keyword.lower()
    for lines in pages_lines:
        for line in lines:
            if keyword in line.lower():
                return lines
    return []

def find_page_with_deposits(pages_lines):
    for lines in pages_lines:
        for line in lines:
            values = re.findall(r"-?\$?\d[\d,]*\.\d{2}", line)
            if len(values) >= 4:
                return lines
    return []
def extract_deposit_row(lines):
    """
    Finds the row that contains all deposit numbers and returns them as a list.
    """
    for line in lines:
        # line with 4 monetary values
        values = re.findall(r"-?\$?\d[\d,]*\.\d{2}", line)
        if len(values) == 4:
            return [v.replace("$", "").replace(",", "") for v in values]
    return [None, None, None, None]
    return None

def extract_policy_number_anywhere(pages_lines):
    for lines in pages_lines:
        for line in lines:
            match = re.search(r"\b(\d{6,})\b", line)
            if match:
                return match.group(1)
    return None

def extract_single_after_label(lines, label):
    for i, line in enumerate(lines):
        if line.strip().lower() == label.lower():
            return lines[i + 1] if i + 1 < len(lines) else None
    return None

def extract_block(lines, start_label, stop_labels):
    collecting = False
    collected = []

    for line in lines:
        if line.strip().lower() == start_label.lower():
            collecting = True
            continue

        if collecting:
            if line.strip() in stop_labels:
                break
            collected.append(line)

    return " ".join(collected).strip() if collected else None



def extract_owner_fields_from_lines(lines):
    owner = {
        "owner_name": None,
        "address": None,
        "phone": None,
        "email": None,
    }

    # 1. Find Owner section start
    try:
        start = lines.index("Owner")
    except ValueError:
        return owner  # Owner section not found

    owner_lines = lines[start + 1:]

    address_lines = []
    collecting_address = False

    for line in owner_lines:
        l = line.lower()

        # Stop if footer reached
        if l.startswith("generated on"):
            break

        # Owner Name (inline)
        if l.startswith("name "):
            owner["owner_name"] = line.replace("Name", "", 1).strip()
            continue

        # Address (inline + multiline)
        if l.startswith("address "):
            collecting_address = True
            address_lines.append(line.replace("Address", "", 1).strip())
            continue

        if collecting_address:
            if l.startswith("home phone") or l.startswith("email"):
                collecting_address = False
            elif l in {"additional advisor information", "owner information"}:
                continue
            else:
                address_lines.append(line)
                continue

        # Home Phone (inline)
        if l.startswith("home phone"):
            owner["phone"] = line.replace("Home Phone", "", 1).strip()
            continue

        # Email (inline)
        if l.startswith("email"):
            owner["email"] = line.replace("Email", "", 1).strip()
            continue

    if address_lines:
        owner["address"] = " ".join(address_lines)

    return owner




def extract_policy_data(pdf_path: str) -> dict:
    data = {}

    with pdfplumber.open(pdf_path) as pdf:
        # ---------- PAGE 1 ----------
        pages_lines = get_all_pages_lines(pdf)

        # ---------- POLICY HEADER / DEPOSITS ----------
        data["policy_number"] = extract_policy_number_anywhere(pages_lines)

        # ✅ Contract type (best effort)
        header_lines = find_page_with_keyword(pages_lines, "Contract Type")
        data["contract_type"] = extract_single_after_label(
            header_lines, "Contract Type"
        )

        # ✅ Deposits (pattern-based, NOT header-based)
        deposit_lines = find_page_with_deposits(pages_lines)
        deposits = extract_deposit_row(deposit_lines)

        data["total_deposits"] = deposits[0]
        data["total_withdrawals"] = deposits[1]
        data["net_deposits"] = deposits[2]
        data["market_value"] = deposits[3]

        # ---------- OWNER SECTION ----------
        owner_page_lines = find_page_with_keyword(
            pages_lines, "Owner"
        )

        owner_data = extract_owner_fields_from_lines(owner_page_lines)
        data.update(owner_data)
    return data
    
def append_to_csv1(data: dict, csv_path: str):
    df = pd.DataFrame([data])

    if os.path.exists(csv_path):
        df.to_csv(csv_path, mode="a", header=False, index=False)
    else:
        df.to_csv(csv_path, index=False)