import faiss
from sentence_transformers import SentenceTransformer
import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from preprocess import *
from typing import List, Dict


def create_faiss_index(chunks: List[Dict], model_name: str = "all-MiniLM-L6-v2") -> faiss.IndexFlatL2:
    """Creates a FAISS index and stores chunk embeddings."""
    model = SentenceTransformer(model_name)
    embeddings = model.encode([chunk["chunk"] for chunk in chunks], convert_to_numpy=True)
    index = faiss.IndexFlatL2(embeddings.shape[1])
    index.add(embeddings)
    return index


if __name__ == "__main__":
    directory = "./documents"  # Change to your directory path
    pdf_texts = load_pdfs_from_directory(directory)
    all_chunks = []
    
    for title, pages in pdf_texts.items():
        for page_nb, text in pages.items():
            all_chunks.extend(chunk_text(text, page_nb, title, max_chunk_size=100))
    
    index = create_faiss_index(all_chunks)
    print("FAISS index created with", index.ntotal, "chunks.")