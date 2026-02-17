import pdfplumber
import re
import pandas as pd
import os
LIFE_FIELDS = [
    "policy_number",
    "product_name",

    "face_amount",
    "death_benefit",
    "accidental_death_benefit",
    "tax_indicator",

    "coverage_status",
    "effective_date",
    "premium_end_date",
    "policy_paid_to_date",

    "premium_mode",
    "premium_amount",
    "minimum_premium",
    "next_payment_date",
    "billing_method",

    "owner_name",
    "insured_name",
    "date_of_birth",
    "sex"
]

GENERAL_FIELDS = [
    "policy_number",
    "contract_type",
    "total_deposits",
    "total_withdrawals",
    "net_deposits",
    "market_value",
    "maturity_date",
    "owner_name",
    "address",
    "phone",
    "email",
    "sex",
    "date_of_birth",
]


def normalize(text):
    return " ".join(text.replace("\u00a0", " ").split())


def extract_money(text):
    match = re.search(r"-?\$?\d[\d,]*\.\d{2}", text)
    if match:
        return match.group(0).replace("$", "").replace(",", "")
    return None

def get_all_pages_lines(pdf):
    pages_lines = []
    for page in pdf.pages:
        text = page.extract_text() or ""
        pages_lines.append(normalize(text))
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



def get_all_pages_lines_from_pdf(pdf_path: str) -> list[list[str]]:
    """
    Extracts normalized text lines from all pages of a PDF.

    Returns:
        List of pages, where each page is a list of cleaned text lines.
        Example:
        [
            ["Line 1 page 1", "Line 2 page 1"],
            ["Line 1 page 2", "Line 2 page 2"],
            ...
        ]
    """
    pages_lines = []

    with pdfplumber.open(pdf_path) as pdf:
        for page in pdf.pages:
            text = page.extract_text() or ""
            lines = [
                line.strip()
                for line in text.splitlines()
                if line.strip()
            ]
            pages_lines.append(lines)

    return pages_lines



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




def extract_policy_data(pages_lines):
    data = {k: None for k in GENERAL_FIELDS}

    # ✅ Flatten and normalize
    all_lines = [
        normalize(line)
        for page in pages_lines
        for line in page
        if line.strip()
    ]

    # ✅ Policy number (multiple formats supported)
    for line in all_lines:
        match = re.search(r"\((\d{6,})\)", line)
        if match:
            data["policy_number"] = match.group(1)
            break

        match = re.search(r"(\d{6,})\)", line)
        if match:
            data["policy_number"] = match.group(1)
            break
        match = re.search(r"policy\s*number\s*(\d{6,})", line, re.I)
        if match:
            data["policy_number"] = match.group(1)
            break
        match = re.fullmatch(r"\d{6,}", line.strip())
        if match:
            data["policy_number"] = match.group(0)
            break

    # ✅ Contract Type
    for i, line in enumerate(all_lines):
        if line == "Contract Type" and i + 1 < len(all_lines):
            data["contract_type"] = all_lines[i + 1]

    # ✅ Deposit values (label or 4-value row)
    for line in all_lines:
        if line.startswith("Total Deposits"):
            data["total_deposits"] = extract_money(line)

        elif line.startswith("Total Withdrawals"):
            data["total_withdrawals"] = extract_money(line)

        elif line.startswith("Net Deposits"):
            data["net_deposits"] = extract_money(line)

        elif line.startswith("Market Value"):
            data["market_value"] = extract_money(line)

    # ✅ Handle single-line 4 deposit values
    for line in all_lines:
        values = re.findall(r"-?\$?\d[\d,]*\.\d{2}", line)
        if len(values) == 4:
            data["total_deposits"] = values[0].replace("$", "").replace(",", "")
            data["total_withdrawals"] = values[1].replace("$", "").replace(",", "")
            data["net_deposits"] = values[2].replace("$", "").replace(",", "")
            data["market_value"] = values[3].replace("$", "").replace(",", "")
            break

    # ✅ Contract Guarantee Values
    for line in all_lines:
        if line.startswith("Maturity Date"):
            data["maturity_date"] = line.replace("Maturity Date", "").strip()

    # ✅ Owner section
    for i, line in enumerate(all_lines):
        if line.lower().startswith("owner"):
            for j in range(i + 1, min(i + 15, len(all_lines))):

                l = all_lines[j].lower()

                if l.startswith("name "):
                    data["owner_name"] = all_lines[j][5:].strip()

                elif l.startswith("address "):
                    address_lines = []
                    address_lines.append(all_lines[j][8:].strip())

                    for k in range(j + 1, min(j + 8, len(all_lines))):
                        next_line = all_lines[k].lower()

                        # ✅ Stop on these markers
                        if next_line.startswith((
                            "home phone",
                            "email",
                            "owner information",
                            "additional advisor information",
                            "values",
                            "annuitant",
                        )):
                            break

                        address_lines.append(all_lines[k])

                    data["address"] = " ".join(address_lines)

                elif l.startswith("home phone"):
                    data["phone"] = all_lines[j].replace("Home Phone", "").strip()

                elif l.startswith("email"):
                    data["email"] = all_lines[j].replace("Email", "").strip()

            break

    # ✅ Sex & DOB (two formats supported)

    # Format 1: separate lines
    for i, line in enumerate(all_lines):
        if line == "Sex" and i + 1 < len(all_lines):
            data["sex"] = all_lines[i + 1]

        elif line == "Date of Birth" and i + 1 < len(all_lines):
            dob = all_lines[i + 1]
            if ", " in dob:
                data["date_of_birth"] = dob.split(", ", 1)[-1]
            else:
                data["date_of_birth"] = dob

    # Format 2: combined line
    for i, line in enumerate(all_lines):
        if line == "Sex Date of Birth" and i + 1 < len(all_lines):
            combined = all_lines[i + 1]
            parts = combined.split(" ", 1)
            if len(parts) == 2:
                data["sex"] = parts[0]
                dob_text = parts[1]
                if ", " in dob_text:
                    data["date_of_birth"] = dob_text.split(", ", 1)[-1]
                else:
                    data["date_of_birth"] = dob_text

    return data
    



def find_lines_with_keyword(pages_lines, keyword):
    for lines in pages_lines:
        for line in lines:
            if keyword.lower() in line.lower():
                return lines
    return []


def extract_inline_value(lines, label):
    for line in lines:
        if line.lower().startswith(label.lower()):
            return line.replace(label, "", 1).strip()
    return None

def value_after_label(lines, label):
    for i, line in enumerate(lines):
        if line.strip().lower() == label.lower():
            return lines[i + 1] if i + 1 < len(lines) else None
    return None



def extract_life_policy_data(pages_lines):
    data = {k: None for k in LIFE_FIELDS}

    # ---------- FLATTEN ----------
    all_lines = [line.strip() for page in pages_lines for line in page if line.strip()]

    # ---------- POLICY NUMBER & PRODUCT ----------
    for i, line in enumerate(all_lines):
        m = re.search(r"\((\d{6,})\)", line)
        if m:
            policy_number = m.group(1)
            data["policy_number"] = policy_number
            if line.strip() != f"({policy_number})":
                data["product_name"] = line.replace(f"({policy_number})", "").strip()

        # ✅ Case 2: number alone on next line (8005 series)
            elif i > 0:
                data["product_name"] = all_lines[i - 1]
            break

    # ---------- COVERAGE / PAYMENTS / ADDITIONAL ----------
    for line in all_lines:
        if line.startswith("Face Amount"):
            data["face_amount"] = line.replace("Face Amount", "").strip()

        elif line.startswith("Death Benefit"):
            data["death_benefit"] = line.replace("Death Benefit", "").strip()

        elif line.startswith("Accidental Death Benefit"):
            data["accidental_death_benefit"] = line.replace(
                "Accidental Death Benefit", ""
            ).strip()

        elif line.startswith("Tax Indicator"):
            data["tax_indicator"] = line.replace("Tax Indicator", "").strip()

        elif line.startswith("Coverage Status"):
            data["coverage_status"] = line.replace("Coverage Status", "").strip()

        elif line.startswith("Effective Date"):
            data["effective_date"] = line.replace("Effective Date", "").strip()

        elif line.startswith("Premium End Date"):
            data["premium_end_date"] = line.replace("Premium End Date", "").strip()

        # ---------- PAYMENTS ----------
        elif line.startswith("Method "):
            data["billing_method"] = line.replace("Method", "").strip()

        elif line.startswith("Premium Mode"):
            data["premium_mode"] = line.replace("Premium Mode", "").strip()

        elif line.startswith("Next Payment Date"):
            match = re.search(r"Next Payment Date (.+)", line)
            if match:
                data["next_payment_date"] = match.group(1).strip()

        # ✅ avoid "Total Amount Billed"
        elif re.fullmatch(r"Amount Billed \$[\d,]+\.\d{2}", line):
            data["premium_amount"] = line.replace("Amount Billed", "").strip()

        # ---------- ADDITIONAL ----------
        elif line.startswith("Minimum Premium"):
            data["minimum_premium"] = line.replace("Minimum Premium", "").strip()

        elif line.startswith("Policy Paid to Date"):
            data["policy_paid_to_date"] = line.replace(
                "Policy Paid to Date", ""
            ).strip()
   # ---------- INSURED ----------

# 1️⃣ Inline format: "Insured John Doe"
    for line in all_lines:
        if line.startswith("Insured "):
            data["insured_name"] = line.replace("Insured", "").strip()
            break

    # 2️⃣ Fallback: "Insured Information" section
    if not data["insured_name"]:
        for i, line in enumerate(all_lines):
            if line == "Insured Information":
                for j in range(i + 1, min(i + 6, len(all_lines))):
                    candidate = all_lines[j]

                    if candidate in {
                        "Coverage Number Smoker Status Age",
                        "Sex",
                        "Date of Birth",
                        "Additional Advisor Information",
                    }:
                        continue

                    data["insured_name"] = candidate.strip()
                    break
                break
    for i , line in enumerate(all_lines):
        if line == "Sex" and i + 1 < len(all_lines):
            data["sex"] = all_lines[i + 1]

        elif line == "Date of Birth" and i + 1 < len(all_lines):
            data["date_of_birth"] = all_lines[i + 1]

    # ---------- OWNER ----------
    for i, line in enumerate(all_lines):
        if line == "Owner":
            for sub in all_lines[i + 1 : i + 15]:
                if sub.startswith("Name"):
                    data["owner_name"] = sub.replace("Name", "").strip()
                    break
            break

    # ---------- VALIDATION ----------
    required = ["policy_number", "product_name", "insured_name", "owner_name"]
    missing = [f for f in required if not data.get(f)]

    if missing:
        raise ValueError(f"Missing LIFE fields: {missing}")

    return data