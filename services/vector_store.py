from sentence_transformers import SentenceTransformer
import faiss
import numpy as np

# Load embedding model (runs once)
model = SentenceTransformer("all-MiniLM-L6-v2")


def create_vector_store(chunks):
    # Convert text → embeddings
    embeddings = model.encode(chunks)

    # Convert to numpy array
    embeddings = np.array(embeddings)

    # Create FAISS index
    dimension = embeddings.shape[1]
    index = faiss.IndexFlatL2(dimension)

    # Store embeddings
    index.add(embeddings)

    return index, embeddings, chunks


def retrieve_chunks(query, index, chunks, top_k=3):
    # ✅ Safety check — don't request more chunks than exist
    top_k = min(top_k, len(chunks))

    # Convert query → embedding
    query_embedding = model.encode([query])

    # Search in FAISS
    D, I = index.search(query_embedding, top_k)

    # ✅ Filter out -1 indices (FAISS returns -1 when results are missing)
    results = [chunks[i] for i in I[0] if i != -1]

    return results