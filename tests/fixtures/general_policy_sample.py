from reportlab.lib.pagesizes import LETTER
from reportlab.pdfgen import canvas
import os


OUTPUT_PATH = "sample_pdfs/general_policy_sample.pdf"


def create_mock_general_policy_pdf(path):
    c = canvas.Canvas(path, pagesize=LETTER)
    width, height = LETTER

    y = height - 40

    # ----- HEADER -----
    c.drawString(40, y, "General Policy Statement")
    y -= 20

    c.drawString(40, y, "(600987675)")
    y -= 20

    c.drawString(40, y, "Contract Type")
    y -= 15
    c.drawString(40, y, "Universal Life")
    y -= 30

    # ----- DEPOSITS -----
    c.drawString(40, y, "Deposits Summary")
    y -= 20

    # ✅ line with 4 monetary values (important)
    c.drawString(
        40,
        y,
        "\$10,000.00 \$2,000.00 \$8,000.00 \$12,500.00"
    )
    y -= 40

    # ----- OWNER SECTION -----
    c.drawString(40, y, "Owner")
    y -= 20

    c.drawString(40, y, "Name John Doe")
    y -= 15

    c.drawString(40, y, "Address 123 Main Street")
    y -= 15
    c.drawString(40, y, "Toronto ON M1M 1M1")
    y -= 15

    c.drawString(40, y, "Home Phone 416-555-1234")
    y -= 15

    c.drawString(40, y, "Email john.doe@example.com")
    y -= 30

    c.drawString(40, y, "Generated on 2024-01-01")

    c.showPage()
    c.save()


if __name__ == "__main__":
    os.makedirs("sample_pdfs/", exist_ok=True)
    create_mock_general_policy_pdf(OUTPUT_PATH)
    print(f"Created {OUTPUT_PATH}")