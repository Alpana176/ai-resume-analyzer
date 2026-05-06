import os
import pdfplumber

def extract_text_from_pdf(file_path):
    if not os.path.exists(file_path):
        return "ERROR: File not found at path: " + file_path

    text = ""

    try:
        with pdfplumber.open(file_path) as pdf:
            for page in pdf.pages:
                content = page.extract_text()
                if content:
                    text += content
    except Exception as e:
        return "ERROR: Could not read PDF: " + str(e)

    if not text.strip():
        return "ERROR: Could not extract any text from PDF"

    print("📄 Extracted Text Preview:", text[:300])
    return text.strip()