import unittest
import os
from personal_rag.rag.retriever import Retriever

class TestRetriever(unittest.TestCase):
    def __init__(self, methodName = "runTest"):
        super().__init__(methodName)
        self.retriever = Retriever(db_path="./data/test_database_files/retriever.db", index_path="./data/test_database_files/faiss.index")

    def test_delete_document(self):
        # Assuming you have a document with ID 1 in your database
        doc_id = 1
        self.retriever.delete_document(doc_id)
        result = self.retriever.db.fetch_document(doc_id)
        self.assertIsNone(result, "Document should be deleted and not retrievable.") 
    
    def test_clear_index(self):
        self.retriever.clear_index()
        self.assertEqual(len(self.retriever.doc_ids), 0, "Index should be cleared and contain no document IDs.")
        self.assertEqual(len(self.retriever.file_metadata["files"]), 0, "File metadata should be cleared and contain no files.")
        self.assertTrue(os.path.exists(self.retriever.index_path), "Index file should exist after clearing index.")
        self.assertTrue(os.path.exists(self.retriever.file_metadata_path), "File metadata should exist after clearing index.")
        self.assertEqual(self.retriever.index.ntotal, 0, "Index should contain no vectors after clearing.")
        
        
    def test_add_document(self):
        # Assuming you have a valid header, chunk, and embedding
        header = "Test Header"
        chunk = "Test Chunk"
        filename = "test_file"
        nb_vectors_before = self.retriever.index.ntotal
        self.retriever.add_document(header, chunk, filename)
        self.assertEqual(self.retriever.index.ntotal, nb_vectors_before + 1, "Index should contain one more vector after adding a document.")
        
        
    
        
if __name__ == '__main__':
    unittest.main()