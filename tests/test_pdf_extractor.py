from src.pdf_extractor import extract_policy_data

def test_extract_policy_data_from_sample_pdf():
    pdf_path = "sample_pdfs/sample_policy.pdf"

    data = extract_policy_data(pdf_path)

    # Basic existence checks
    assert data["policy_number"] is not None
    assert data["contract_type"] is not None

    # Numeric fields
    assert data["total_deposits"] is not None
    assert data["total_withdrawals"] is not None
    assert data["net_deposits"] is not None
    assert data["market_value"] is not None

    # Owner fields
    assert data["owner_name"] is not None
    assert data["address"] is not None
    assert data["phone"] is not None
    assert "@" in data["email"]