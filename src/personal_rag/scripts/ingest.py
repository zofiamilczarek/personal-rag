import sys
import os
import argparse
# from personal_rag.database import Database
from personal_rag.rag import Retriever
from personal_rag.preprocess import get_pdf_chunks
from pathlib import Path
import json

def __get_args():
    
    parser = argparse.ArgumentParser()
    
    parser.add_argument(
        "path",
        type = str,
        help = "The path to the folder containing the preprocessed pdf files in json format to be used in the RAG pipeline",
    )
    
    parser.add_argument(
        "--clear-index",
        action="store_true",
        help="If set, the existing FAISS index will be cleared before indexing the documents."
    )
    
    parser.add_argument(
        "--preprocess",
        action="store_true",
        help="If set, the script will first preprocess the pdf files"
    )
    
    return parser.parse_args()
    

# TODO: create a test here
def create_faiss_index(data_path, clear_index = True):
    path = Path(data_path)
    rtr = Retriever(db_path="./data/test_database_files/retriever.db", index_path="./data/test_database_files/faiss.index")
    
    if not path.is_dir():
            raise NotADirectoryError(f"The provided path '{path}' is not a directory.")
    
    if clear_index:
        rtr.clear_index()
    
    for file_path in path.iterdir():
        # ignore files that aren't pdfs
        if Path(file_path).suffix != '.json':
            continue 
        with open(str(file_path), 'r') as f:
            chunks = json.load(f)
        rtr.add_documents_bulk(chunks)
        
    return rtr


def main():
    """
    1. parse agrs
        a. should have an option to wipe the database clean and repopulate it
    2. load the pdf chunks
    3. create a retriever
    3. ingest all the chunks into the retriever
    
        - if the document was added, add it to some management file that keeps track of which files have been added 
    """
    
    args = __get_args()
    
    create_faiss_index(args.path, args.clear_index)

main()