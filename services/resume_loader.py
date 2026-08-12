import os
import pdfplumber


def extract_text_from_pdf(file_path):
    """
    Extract text from all pages of a PDF resume.

    Returns:
        str: Extracted resume text or an error message.
    """

    if not file_path:
        return "ERROR: No file path provided."

    if not os.path.exists(file_path):
        return f"ERROR: File not found at path: {file_path}"

    text_parts = []

    try:

        with pdfplumber.open(file_path) as pdf:

            for page_number, page in enumerate(
                pdf.pages,
                start=1
            ):

                content = page.extract_text()

                if content:
                    text_parts.append(
                        content
                    )

    except Exception as e:

        return f"ERROR: Could not read PDF: {str(e)}"

    # Combine pages
    text = "\n\n".join(text_parts)

    # Validate extracted content
    if not text.strip():

        return (
            "ERROR: Could not extract any text from PDF. "
            "The PDF may contain scanned images instead of text."
        )

    print(
        f"📄 Successfully extracted text from "
        f"{len(text_parts)} page(s)"
    )

    print(
        "📄 Text preview:",
        text[:300]
    )

    return text.strip()