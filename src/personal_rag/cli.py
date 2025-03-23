import cmd
import os
import json
from personal_rag.rag import Retriever
from pathlib import Path
from personal_rag.preprocess import get_pdf_chunks
from personal_rag.preprocess import create_faiss_index


# run ingest

# create the Retriever object

# make a nice UI to make queries and such

class STYLES:
    pass


class PersonalRagCLI(cmd.Cmd):
    prompt = 'PersonalRAG>> '
    intro = 'Welcome to PersonalRAG. Type "help" for available commands.'
    
    def __init__(self):
        super().__init__()
        self.current_directory = os.getcwd()

    def do_load_my_data(self, dirpath):
        """
        Loads and preprocessed your pdfs to be ready to use with the RAG system. Requires a path to the folder with your pdfs
        For example:
            load_my_data /home/documents/my_pdfs
        """
        
        path = Path(dirpath)
                
        # TODO: WEEWOOWEEWOO this throws an error when it shouldnt
        # if path.is_dir():
        #     raise NotADirectoryError(f"The provided path '{dirpath}' is not a directory.")
        
        # preprocess
        for file_path in path.iterdir():
            # ignore files that aren't pdfs
            if Path(file_path).suffix != '.pdf':
                continue
            try:
                chunks = get_pdf_chunks(str(file_path))
                file_name = file_path.stem
                with open(f'./data/processed/{file_name}_chunks.json', 'w') as f:
                    f.write(json.dumps(chunks))
            except:
                print(f"failed to load {file_path}")
        
        # ingest
        create_faiss_index("./data/processed")
        
        
    def do_query(self, query):
        """
        Allows you to ask a query to Retriever. It will retrieve document chunks with relevant text and give you the pages 
        """
        print(query)
        
    def do_rag_query(self, query):
        pass
    
    def postcmd(self, stop, line):
        print()  # Add an empty line for better readability
        return stop
    
    
if __name__ == '__main__':
    PersonalRagCLI().cmdloop()