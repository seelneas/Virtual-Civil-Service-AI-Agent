from pdf2image import convert_from_path
import pytesseract
import os

def extract_text_from_file(file_path, lang="eng"):
    if not os.path.exists(file_path):
        return ""

    text = ""
    try:
        if file_path.lower().endswith(".pdf"):
            # Convert PDF pages to images
            pages = convert_from_path(file_path)
            for page in pages:
                text += pytesseract.image_to_string(page, lang=lang) + "\n"
        else:
            from PIL import Image
            img = Image.open(file_path)
            text = pytesseract.image_to_string(img, lang=lang)
    except Exception as e:
        print("OCR error:", e)

    return text.strip()
