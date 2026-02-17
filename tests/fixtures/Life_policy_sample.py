from reportlab.lib.pagesizes import LETTER
from reportlab.pdfgen import canvas
import os


OUTPUT_PATH = "sample_pdfs/life_policy_sample.pdf"


def create_mock_life_policy_pdf(path):
    c = canvas.Canvas(path, pagesize=LETTER)
    width, height = LETTER

    y = height - 40

    # ----- HEADER -----
    c.drawString(40, y, "Secure Life Insurance Plan")
    y -= 20
    c.drawString(40, y, "(800012345)")
    y -= 30

    # ----- COVERAGE -----
    c.drawString(40, y, "Coverage")
    y -= 20

    c.drawString(40, y, "Face Amount \$250,000")
    y -= 15
    c.drawString(40, y, "Death Benefit \$250,000")
    y -= 15
    c.drawString(40, y, "Accidental Death Benefit \$500,000")
    y -= 15
    c.drawString(40, y, "Tax Indicator Taxable")
    y -= 15
    c.drawString(40, y, "Coverage Status Active")
    y -= 15
    c.drawString(40, y, "Effective Date 2020-01-01")
    y -= 15
    c.drawString(40, y, "Premium End Date 2040-01-01")
    y -= 30

    # ----- PAYMENTS -----
    c.drawString(40, y, "Payments")
    y -= 20

    c.drawString(40, y, "Method Monthly")
    y -= 15
    c.drawString(40, y, "Premium Mode Monthly")
    y -= 15
    c.drawString(40, y, "Next Payment Date 2026-01-01")
    y -= 15
    c.drawString(40, y, "Amount Billed \$150.00")
    y -= 30

    # ----- ADDITIONAL INFO -----
    c.drawString(40, y, "Additional Advisor Information")
    y -= 20

    c.drawString(40, y, "Minimum Premium \$100.00")
    y -= 15
    c.drawString(40, y, "Policy Paid to Date 2025-12-01")
    y -= 30

    # ----- OWNER -----
    c.drawString(40, y, "Owner")
    y -= 20
    c.drawString(40, y, "Name Jane Smith")
    y -= 30

    # ----- INSURED -----
    c.drawString(40, y, "Insured")
    y -= 20
    c.drawString(40, y, "Insured Jane Smith")
    y -= 15
    c.drawString(40, y, "Sex Female")
    y -= 15
    c.drawString(40, y, "Date of Birth 1985-06-15")

    c.showPage()
    c.save()


if __name__ == "__main__":
    os.makedirs("sample_pdfs/", exist_ok=True)
    create_mock_life_policy_pdf(OUTPUT_PATH)
    print(f"Created {OUTPUT_PATH}")