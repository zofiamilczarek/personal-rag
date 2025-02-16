import faiss
import numpy as np
from sentence_transformers import SentenceTransformer

import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from database import Database

class Retriever:
    def __init__(self, db_path="./database/retriever.db", index_path="./rag/faiss.index", model_name="all-MiniLM-L6-v2"):
        self.db = Database(db_path)
        self.index_path = index_path
        self.model = SentenceTransformer(model_name)
        self.index = faiss.IndexFlatL2(self.model.get_sentence_embedding_dimension())
        self.doc_ids = []

        if os.path.exists(self.index_path):
            self.load_index()
        else:
            self.save_index()

    def load_index(self):
        try:
            self.index = faiss.read_index(self.index_path)
        except:
            pass

    def save_index(self):
        faiss.write_index(self.index, self.index_path)

    def add_document(self, header, chunk):
        embedding = self.model.encode(chunk).astype(np.float32)
        doc_id = self.db.add_document(header, chunk, embedding)
        self.index.add(np.array([embedding]))
        self.doc_ids.append(doc_id)
        self.save_index()

    def add_documents_bulk(self, documents):
        embeddings = [(header, chunk, self.model.encode(chunk).astype(np.float32)) for header, chunk in documents]
        doc_ids = self.db.add_documents_bulk(embeddings)
        self.index.add(np.array([emb[2] for emb in embeddings]))
        self.doc_ids.extend(doc_ids)
        self.save_index()

    def retrieve(self, query, k=5):
        query_embedding = self.model.encode(query).astype(np.float32).reshape(1, -1)
        distances, indices = self.index.search(query_embedding, k)
        results = []
        for i in range(len(indices[0])):
            if indices[0][i] == -1:
                continue
            doc_id = self.doc_ids[indices[0][i]]
            row = self.db.fetch_document(doc_id)
            if row:
                results.append({"header": row[0], "chunk": row[1], "score": distances[0][i]})
        return results

    def delete_document(self, doc_id):
        self.db.delete_document(doc_id)
        self._rebuild_index()

    def _rebuild_index(self):
        self.index = faiss.IndexFlatL2(self.model.get_sentence_embedding_dimension())
        self.doc_ids = []
        for doc_id, embedding_blob in self.db.fetch_all_embeddings():
            embedding = np.frombuffer(embedding_blob, dtype=np.float32)
            self.index.add(np.array([embedding]))
            self.doc_ids.append(doc_id)
        self.save_index()

if __name__ == "__main__":
    rtr = Retriever()
    
    
    
"""
I want to create my own RAG pipeline. First, I need the retriever. I want it to have the following features:
- it will need to be able to retrieve chunks from a large database. Therefore, the querying should be efficient and the database cannot be loaded into the program memory
- the text chunk needs to be retrieved with a relevant header
- the retriever should return k most relevant chunks, k being a variable
- I need to be able to update my database, where I remove or add files
Write python code that satisfies these.
"""