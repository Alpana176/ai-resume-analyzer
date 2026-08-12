from sentence_transformers import SentenceTransformer
import faiss
import numpy as np


# ---------------------------------------------------------
# Embedding model
# ---------------------------------------------------------

MODEL_NAME = "all-MiniLM-L6-v2"

model = SentenceTransformer(
    MODEL_NAME
)


# ---------------------------------------------------------
# Create vector store
# ---------------------------------------------------------

def create_vector_store(chunks):
    """
    Convert resume chunks into embeddings and
    create a FAISS vector index.

    Normalized embeddings + inner product provide
    cosine-similarity based retrieval.
    """

    if not chunks:

        raise ValueError(
            "Cannot create vector store: "
            "no text chunks provided."
        )


    # -----------------------------------------------------
    # Generate embeddings
    # -----------------------------------------------------

    embeddings = model.encode(
        chunks,
        convert_to_numpy=True,
        normalize_embeddings=True,
        show_progress_bar=False
    )


    # -----------------------------------------------------
    # Convert to float32
    # -----------------------------------------------------

    embeddings = np.asarray(
        embeddings,
        dtype="float32"
    )


    # -----------------------------------------------------
    # Determine vector dimension
    # -----------------------------------------------------

    dimension = embeddings.shape[1]


    # -----------------------------------------------------
    # FAISS index
    #
    # Because embeddings are normalized,
    # Inner Product ≈ Cosine Similarity
    # -----------------------------------------------------

    index = faiss.IndexFlatIP(
        dimension
    )


    # -----------------------------------------------------
    # Add vectors
    # -----------------------------------------------------

    index.add(
        embeddings
    )


    print(
        f"🔢 Added {len(chunks)} vectors "
        f"to FAISS index"
    )

    print(
        f"📐 Embedding dimension: {dimension}"
    )


    return (
        index,
        embeddings,
        chunks
    )


# ---------------------------------------------------------
# Retrieve relevant chunks
# ---------------------------------------------------------

def retrieve_chunks(
    query,
    index,
    chunks,
    top_k=5
):
    """
    Retrieve the most semantically relevant
    resume chunks for a query.

    Returns:
        [
            {
                "text": "...",
                "score": 0.82
            }
        ]
    """

    if not query or not query.strip():
        return []

    if not chunks:
        return []

    if index is None:
        return []


    # -----------------------------------------------------
    # Prevent requesting more results than available
    # -----------------------------------------------------

    top_k = min(
        top_k,
        len(chunks)
    )


    # -----------------------------------------------------
    # Encode query
    # -----------------------------------------------------

    query_embedding = model.encode(
        [query],
        convert_to_numpy=True,
        normalize_embeddings=True,
        show_progress_bar=False
    )


    query_embedding = np.asarray(
        query_embedding,
        dtype="float32"
    )


    # -----------------------------------------------------
    # FAISS search
    # -----------------------------------------------------

    scores, indices = index.search(
        query_embedding,
        top_k
    )


    # -----------------------------------------------------
    # Build structured results
    # -----------------------------------------------------

    results = []

    for score, idx in zip(
        scores[0],
        indices[0]
    ):

        if idx == -1:
            continue

        results.append(
            {
                "text": chunks[idx],
                "score": float(score)
            }
        )


    print(
        f"🔎 Retrieved {len(results)} relevant chunks"
    )


    return results