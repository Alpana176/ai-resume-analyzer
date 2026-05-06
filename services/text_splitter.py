def split_text(text, chunk_size=500, overlap=100):
    # ✅ Safety check — empty or None input
    if not text or text.strip() == "":
        return []

    chunks = []
    start = 0
    text_length = len(text)

    while start < text_length:
        end = start + chunk_size
        chunk = text[start:end].strip()

        # ✅ Only keep chunks with meaningful content
        if len(chunk) > 50:
            chunks.append(chunk)

        start += chunk_size - overlap

    return chunks