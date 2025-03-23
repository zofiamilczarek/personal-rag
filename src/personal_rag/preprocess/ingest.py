from personal_rag.rag import Retriever
from pathlib import Path
import json

# TODO: create a test here
# maybe this should be part of the Retriever class
def create_faiss_index(data_path, 
                       clear_index = True,
                       db_path = "./data/database_files/retriever.db",
                       index_path = "./data/database_files/faiss.index"):
    path = Path(data_path)
    rtr = Retriever(db_path=db_path, index_path=index_path)
    
    if not path.is_dir():
            raise NotADirectoryError(f"The provided path '{path}' is not a directory.")
    
    if clear_index:
        rtr.clear_index()
    
    for file_path in path.iterdir():
        suffix = str(Path(file_path).suffix)
        file_name = str(Path(file_path).stem)
        # ignore files that aren't pdfs and that are already in the index
        if (suffix != '.json' or
            file_name in rtr.file_metadata["files"]):
            continue 
        
        with open(str(file_path), 'r') as f:
            chunks = json.load(f)
        
        rtr.add_document_chunks(chunks, file_name)
        
    return rtr