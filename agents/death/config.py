import os

BASE_DIR = os.path.dirname(__file__)
DOCUMENTS_PATH = os.path.join(BASE_DIR, "../../data/documents")
CERTIFICATES_PATH = os.path.join(BASE_DIR, "../../data/certificates")

OCR_LANG = 'amh'  # Amharic language for Tesseract
CERTIFICATE_PREFIX = "DC"  # Death Certificate
