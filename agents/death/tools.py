import os
from datetime import datetime
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
from .config import CERTIFICATES_PATH, CERTIFICATE_PREFIX
from agents.death.ocr_utils import extract_text_from_file
from db.database import get_connection

# Fraud check
def check_duplicate_death(citizen_id):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM death_records WHERE citizen_id=?", (citizen_id,))
    exists = cursor.fetchone() is not None
    conn.close()
    return exists

# Document verification (using OCR)
def verify_document(file_path, required_keywords=[]):
    text = extract_text_from_file(file_path)
    for keyword in required_keywords:
        if keyword not in text:
            return False
    return True

# Certificate generator
def generate_certificate(death_record):
    certificate_number = f"{CERTIFICATE_PREFIX}-{death_record['record_id']:04d}"
    file_name = f"{certificate_number}.pdf"
    file_path = os.path.join(CERTIFICATES_PATH, file_name)

    os.makedirs(CERTIFICATES_PATH, exist_ok=True)

    c = canvas.Canvas(file_path, pagesize=A4)
    c.setFont("Helvetica-Bold", 16)
    c.drawString(100, 800, "Death Certificate")
    c.setFont("Helvetica", 12)
    c.drawString(100, 770, f"Certificate Number: {certificate_number}")
    c.drawString(100, 750, f"Full Name: {death_record['full_name']}")
    c.drawString(100, 730, f"National ID: {death_record['national_id']}")
    c.drawString(100, 710, f"Date of Death: {death_record['date_of_death']}")
    c.drawString(100, 690, f"Place of Death: {death_record['place_of_death']}")
    c.drawString(100, 670, f"Cause of Death: {death_record['cause_of_death']}")
    c.drawString(100, 650, f"Informant: {death_record['informant_name']}")
    c.drawString(100, 630, f"Date Registered: {datetime.now().strftime('%Y-%m-%d')}")
    c.showPage()
    c.save()

    return file_path, certificate_number
