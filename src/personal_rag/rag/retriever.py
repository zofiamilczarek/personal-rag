import faiss
import numpy as np
from sentence_transformers import SentenceTransformer
import os
from personal_rag.database import Database
# from personal_rag.preprocess import get_pdf_chunks
import json


class Retriever: 
    def __init__(self, 
                 db_path="./data/database_files/retriever.db", 
                 index_path="./data/database_files/faiss.index", 
                 model_name="all-MiniLM-L6-v2",):
        
        self.db = Database(db_path)
        self.index_path = index_path
        self.model = SentenceTransformer(model_name)
        self.index = faiss.IndexFlatL2(self.model.get_sentence_embedding_dimension())
        self.doc_ids = []
        self.file_metadata_path = os.path.join(os.path.dirname(index_path), "file_metadata.json")
        self.file_metadata = self._load_file_metadata()
        
        if os.path.exists(self.index_path):
            self.load_index()
        else:
            self.save_index()
    
    def _load_file_metadata(self):
        if os.path.exists(self.file_metadata_path):
            with open(self.file_metadata_path, "r") as f:
                return {"files": set(json.load(f)["files"])}
        return {"files": set()}
    
    def _save_file_metadata(self):
        with open(self.file_metadata_path, "w") as f:
            json.dump({"files": list(self.file_metadata["files"])}, f, indent=4)

    def load_index(self):
        try:
            self.index = faiss.read_index(self.index_path)
            self.doc_ids = [row[0] for row in self.db.fetch_all_embeddings()]
        except:
            self.doc_ids = []

    def save_index(self):
        faiss.write_index(self.index, self.index_path)
        self._save_file_metadata()
        
    def clear_index(self):
        self.index = faiss.IndexFlatL2(self.model.get_sentence_embedding_dimension())
        self.doc_ids = []
        self.file_metadata = {"files": set()}
        self.save_index()

    def add_document(self, header, chunk, file_name):
        embedding = self.model.encode(chunk).astype(np.float32)
        doc_id = self.db.add_document(header, chunk, embedding)
        self.index.add(np.array([embedding]))
        self.doc_ids.append(doc_id)
        self.file_metadata["files"].add(file_name)
        self.save_index()

    def add_document_chunks(self, documents, file_name):
        embeddings = [(str(doc['header']), doc['chunk'], self.model.encode(doc['chunk']).astype(np.float32)) for doc in documents]
        doc_ids = self.db.add_documents_bulk(embeddings)
        self.index.add(np.array([emb[2] for emb in embeddings]))
        self.doc_ids.extend(doc_ids)
        
        self.file_metadata["files"].add(file_name)
        
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
                results.append({
                    "header": row[0],
                    "chunk": row[1],
                    "score": distances[0][i]
                })
        return results
    
    def delete_document(self, doc_id):
        self.db.delete_document(doc_id)
        self._rebuild_index()
        self._cleanup_file_metadata()

    def _cleanup_file_metadata(self):
        remaining_files = set(row[0] for row in self.db.fetch_all_documents())
        self.file_metadata["files"].intersection_update(remaining_files)
        self._save_file_metadata()

    def _rebuild_index(self):
        self.index = faiss.IndexFlatL2(self.model.get_sentence_embedding_dimension())
        self.doc_ids = []
        
        for doc_id, embedding_blob in self.db.fetch_all_embeddings():
            embedding = np.frombuffer(embedding_blob, dtype=np.float32)
            self.index.add(np.array([embedding]))
            self.doc_ids.append(doc_id)
        
        self.save_index()

if __name__ == "__main__":
    rtr = Retriever(db_path="./data/test_database_files/retriever.db", index_path="./data/test_database_files/faiss.index")
    # rtr = Retriever()
    # chunks = get_pdf_chunks("./data/raw_pdfs/nlp_textbook_jurafsky.pdf", max_chunk_size=300)
    # rtr.add_documents_bulk(chunks)
    
    retrieved_chunks = rtr.retrieve("How do LLMs work")
    
    print(*retrieved_chunks, sep="\n\n")