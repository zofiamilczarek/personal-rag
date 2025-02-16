import sqlite3
import numpy as np

class Database:
    def __init__(self, db_path="./database/retriever.db"):
        self.db_path = db_path
        self._init_db()

    def _init_db(self):
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute('''CREATE TABLE IF NOT EXISTS documents (
                                id INTEGER PRIMARY KEY AUTOINCREMENT,
                                header TEXT,
                                chunk TEXT,
                                embedding BLOB
                              )''')
            conn.commit()

    def add_document(self, header, chunk, embedding):
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("INSERT INTO documents (header, chunk, embedding) VALUES (?, ?, ?)",
                           (header, chunk, embedding.tobytes()))
            doc_id = cursor.lastrowid
            conn.commit()
        return doc_id

    def add_documents_bulk(self, documents):
        embeddings = []
        doc_ids = []
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            for header, chunk, embedding in documents:
                cursor.execute("INSERT INTO documents (header, chunk, embedding) VALUES (?, ?, ?)",
                               (header, chunk, embedding.tobytes()))
                doc_ids.append(cursor.lastrowid)
            conn.commit()
        return doc_ids

    def fetch_document(self, doc_id):
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT header, chunk FROM documents WHERE id=?", (doc_id,))
            return cursor.fetchone()

    def fetch_all_embeddings(self):
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT id, embedding FROM documents")
            return cursor.fetchall()

    def delete_document(self, doc_id):
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("DELETE FROM documents WHERE id=?", (doc_id,))
            conn.commit()
            
            
if __name__ == "__main__":
    db = Database()
    