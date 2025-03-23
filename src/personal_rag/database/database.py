import sqlite3
from pathlib import Path


class Database:
    def __init__(self, db_path="./data/database_files/retriever.db"):
        self.db_path = db_path
        directory_path = Path(self.db_path).parents[0]
        directory_path.mkdir(exist_ok=True, parents=True)
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

    def _add_document(self, conn, header, chunk, embedding):
        cursor = conn.cursor()
        cursor.execute("INSERT INTO documents (header, chunk, embedding) VALUES (?, ?, ?)",
                        (header, chunk, embedding.tobytes()))
        doc_id = cursor.lastrowid
        return doc_id

    
    def add_document(self, header, chunk, embedding):
        with sqlite3.connect(self.db_path) as conn:
            doc_id = self._add_document(conn, header, chunk, embedding)
            conn.commit()
        return doc_id

    def add_documents_bulk(self, documents):
        doc_ids = []
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            for header, chunk, embedding in documents:
                doc_id = self._add_document(conn, header, chunk, embedding)
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
    