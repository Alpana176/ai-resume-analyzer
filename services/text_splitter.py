import re


def split_text(
    text,
    chunk_size=800,
    overlap=150
):
    """
    Split resume text into overlapping chunks.

    The splitter attempts to preserve sentence boundaries
    instead of blindly cutting text at arbitrary positions.

    Args:
        text: Resume text
        chunk_size: Maximum approximate characters per chunk
        overlap: Number of overlapping characters

    Returns:
        list[str]: Resume chunks
    """

    # ---------------------------------------------------------
    # Validate input
    # ---------------------------------------------------------

    if not text or not text.strip():
        return []

    if overlap >= chunk_size:
        raise ValueError(
            "overlap must be smaller than chunk_size"
        )


    # ---------------------------------------------------------
    # Normalize whitespace
    # ---------------------------------------------------------

    text = re.sub(
        r"\s+",
        " ",
        text
    ).strip()


    chunks = []

    start = 0
    text_length = len(text)


    # ---------------------------------------------------------
    # Create chunks
    # ---------------------------------------------------------

    while start < text_length:

        end = min(
            start + chunk_size,
            text_length
        )


        # -----------------------------------------------------
        # Try to end at a sentence boundary
        # -----------------------------------------------------

        if end < text_length:

            sentence_end = max(
                text.rfind(".", start, end),
                text.rfind("!", start, end),
                text.rfind("?", start, end)
            )

            # Only use the sentence boundary if
            # it doesn't make the chunk too small.
            if sentence_end > start + chunk_size // 2:

                end = sentence_end + 1


        chunk = text[start:end].strip()


        # -----------------------------------------------------
        # Ignore tiny chunks
        # -----------------------------------------------------

        if len(chunk) >= 100:

            chunks.append(chunk)


        # -----------------------------------------------------
        # Move forward with overlap
        # -----------------------------------------------------

        next_start = end - overlap

        if next_start <= start:
            next_start = end

        start = next_start


    print(
        f"🧩 Created {len(chunks)} resume chunks"
    )

    return chunks