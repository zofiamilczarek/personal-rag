import faiss
import numpy as np
from sentence_transformers import SentenceTransformer
import os
from personal_rag.database import Database
# from personal_rag.preprocess import get_pdf_chunks
import json
import ast
from pathlib import Path


class Retriever:
    def __init__(self,
                 db_path="./data/database_files/retriever.db",
                 index_path="./data/database_files/faiss.index",
                 model_name="BAAI/bge-m3"):
        self.model_name = model_name
        # self.db = Database(db_path)
        self.index_path = index_path
        print("Loading Model")
        self.model = SentenceTransformer(model_name)
        print("Done.")
        self.db = Database(db_path)

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
            json.dump({
                "files": list(self.file_metadata["files"]),
                "model": self.model_name,
                "dimension": self.model.get_sentence_embedding_dimension()
                       }, f, indent=4)

    def load_index(self):
        try:
            self.index = faiss.read_index(self.index_path)
            self.doc_ids = [row[0] for row in self.db.fetch_all_embeddings()]
        except:
            self.doc_ids = []

    def save_index(self):
        if not os.path.exists(os.path.dirname(self.index_path)):
            os.makedirs(os.path.dirname(self.index_path))

        faiss.write_index(self.index, self.index_path)
        self._save_file_metadata()

    def clear_index(self):
        self.index = faiss.IndexFlatL2(self.model.get_sentence_embedding_dimension())
        self.doc_ids = []
        self.file_metadata = {"files": set()}
        self.save_index()

    def add_document_chunks(self, documents, file_name):
        if len(documents):
          embeddings = [(str(doc['header']), doc['chunk'], self.model.encode(doc['chunk']).astype(np.float32)) for doc in documents]
          doc_ids = self.db.add_documents_bulk(embeddings)
          self.index.add(np.array([emb[2] for emb in embeddings]))
          self.doc_ids.extend(doc_ids)

        self.file_metadata["files"].add(file_name)

        self.save_index()

    def index_processed(self, data_path, clear_index = True):
      path = Path(data_path)

      if not path.is_dir():
              raise NotADirectoryError(f"The provided path '{path}' is not a directory.")

      if clear_index:
          self.clear_index()

      for file_path in path.iterdir():
          suffix = str(Path(file_path).suffix)
          file_name = str(Path(file_path).stem)
          # ignore files that aren't pdfs and that are already in the index
          if (suffix != '.json' or
              file_name in self.file_metadata["files"]):
              continue

          with open(str(file_path), 'r') as f:
              chunks = json.load(f)

          self.add_document_chunks(chunks, file_name)


    def retrieve(self, query, k=5):
        query_embedding = self.model.encode(query).astype(np.float32).reshape(1, -1)
        distances, indices = self.index.search(query_embedding, k)
        results = []
        for i in range(len(indices[0])):
            if indices[0][i] == -1:
                continue
            try:
                doc_id = self.doc_ids[indices[0][i]]
            except IndexError:
                print(f"{self.doc_ids=}")
                print(f"{len(self.doc_ids)=}")
                print(f"{indices=}")
                raise IndexError
            row = self.db.fetch_document(doc_id)
            if row:
                results.append({
                    "header": ast.literal_eval(row[0]),
                    "chunk": row[1],
                    "score": distances[0][i]
                })
        return results

    def pretty_retrieve(self,query,k=5):
        results = self.retrieve(query, k=k)
        docs = {}
        for res in results:
            title = res['header']['title']
            page = res['header']['page']
            if title in docs.keys():
                docs[title].append(page)
            else:
                docs[title] = [page]
        return docs

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
    rtr = Retriever(db_path="./data/database_files/retriever.db", index_path="./data/database_files/faiss.index")
    # rtr = Retriever()
    # chunks = get_pdf_chunks("./data/raw_pdfs/nlp_textbook_jurafsky.pdf", max_chunk_size=300)
    # rtr.add_documents_bulk(chunks)

    retrieved_chunks = rtr.retrieve("Machine Yearning", k=20)

    print(*retrieved_chunks, sep="\n\n")
