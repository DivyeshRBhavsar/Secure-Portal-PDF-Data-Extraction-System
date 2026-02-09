from reportlab.lib.pagesizes import LETTER
from reportlab.pdfgen import canvas
import os

os.makedirs("sample_pdfs", exist_ok=True)

pdf_path = "sample_pdfs/sample_policy.pdf"
c = canvas.Canvas(pdf_path, pagesize=LETTER)
width, height = LETTER

y = height - 50

# ---------- PAGE 1 ----------
c.setFont("Helvetica-Bold", 14)
c.drawString(50, y, "Guaranteed Interest Account - 123456789")
y -= 30

c.setFont("Helvetica", 11)
c.drawString(50, y, "Contract Type")
y -= 15
c.drawString(50, y, "TFSA")
y -= 30

c.setFont("Helvetica-Bold", 11)
c.drawString(50, y, "Total Deposits   Total Withdrawals   Net Deposits   Total Market Value")
y -= 15
c.setFont("Helvetica", 11)
c.drawString(50, y, "\$6,000.00   \$6,039.21   -\$39.21   \$0.00")

c.showPage()

# ---------- PAGE 2 (filler) ----------
c.setFont("Helvetica", 11)
c.drawString(50, height - 50, "This page is intentionally left blank.")
c.showPage()

# ---------- PAGE 3 ----------
y = height - 50
c.setFont("Helvetica-Bold", 13)
c.drawString(50, y, "Owner")
y -= 25

c.setFont("Helvetica", 11)
c.drawString(50, y, "Name MS SAMPLE USER")
y -= 20

c.drawString(50, y, "Address 123 Sample Street")
y -= 15
c.drawString(50, y, "Sample City, Province X1X 1X1")
y -= 15
c.drawString(50, y, "Canada")
y -= 25

c.drawString(50, y, "Home Phone 1234567890")
y -= 15
c.drawString(50, y, "Email sample.user@example.com")

c.showPage()
c.save()

print(f"✅ Sample PDF created at {pdf_path}")