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



def retrieve_relevant_chunk(query: str, index: faiss.IndexFlatL2, chunks: List[Dict], model_name: str = "all-MiniLM-L6-v2", k: int = 5) -> List[Dict]:
    """
    Retrieve the top k most relevant chunks from the FAISS index for the given query.

    Args:
        query (str): The search query.
        index (faiss.IndexFlatL2): A FAISS index built from the chunks.
        chunks (List[Dict]): The list of chunk dictionaries corresponding to the embeddings.
        model_name (str): The SentenceTransformer model for encoding the query.
        k (int): Number of top relevant chunks to return.

    Returns:
        List[Dict]: The list of chunk dictionaries most relevant to the query.
    """
    model = SentenceTransformer(model_name)
    query_embedding = model.encode([query], convert_to_numpy=True)
    distances, indices = index.search(query_embedding, k)
    best_indices = indices[0]
    return [chunks[i] for i in best_indices]


if __name__ == "__main__":
    directory = "./pdfs"  # Change to your directory path
    pdf_texts = load_pdfs_from_directory(directory)
    all_chunks = []
    
    for title, pages in pdf_texts.items():
        for page_nb, text in pages.items():
            all_chunks.extend(chunk_text(text, page_nb, title, max_chunk_size=500))
    
    index = create_faiss_index(all_chunks)
    print("FAISS index created with", index.ntotal, "chunks.")
    
    query = "What is tf idf"
    
    chunks = retrieve_relevant_chunk(query, index, all_chunks)
    
    print(*chunks, sep="\n")
    
    
    
"""
I want to create my own RAG pipeline. First, I need the retriever. I want it to have the following features:
- it will need to be able to retrieve chunks from a large database. Therefore, the querying should be efficient and the database cannot be loaded into the program memory
- the text chunk needs to be retrieved with a relevant header
- the retriever should return k most relevant chunks, k being a variable
- I need to be able to update my database, where I remove or add files
Write python code that satisfies these.
"""