import os
from src.pdf_extractor import (
    extract_policy_data,
    extract_life_policy_data,
    get_all_pages_lines_from_pdf,
    LIFE_FIELDS,
    GENERAL_FIELDS,
)

FIXTURES_DIR = "sample_pdfs/"


def test_general_policy_extraction():
    pdf_path = os.path.join(FIXTURES_DIR, "general_policy_sample.pdf")
    
    pages_lines = get_all_pages_lines_from_pdf(pdf_path)
    data = extract_policy_data(pages_lines)

    assert isinstance(data, dict)
    for field in GENERAL_FIELDS:
        assert field in data
    
    print(data)

    # ✅ Basic sanity checks
    assert data["policy_number"] is not None
    if "Total Deposits" in " ".join(sum(pages_lines, [])):
        assert data["total_deposits"] is not None


def test_life_policy_extraction():
    pdf_path = os.path.join(FIXTURES_DIR, "life_policy_sample.pdf")

    pages_lines = get_all_pages_lines_from_pdf(pdf_path)
    data = extract_life_policy_data(pages_lines)

    assert isinstance(data, dict)

    for field in LIFE_FIELDS:
        assert field in data

    assert data["policy_number"] is not None
    assert data["insured_name"] is not None