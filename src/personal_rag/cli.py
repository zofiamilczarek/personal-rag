import cmd
import os
import glob as gb
import json
from personal_rag.rag import Retriever
from pathlib import Path
from personal_rag.preprocess import get_pdf_chunks, preprocess_pdfs_in_directory
from personal_rag.preprocess import create_faiss_index

import readline

readline.set_completer_delims(' \t\n')


def _complete_path(path):
    """A method to handle path autocomplete in a cmd.Cmd interface"""
    if os.path.isdir(path):
        return gb.glob(os.path.join(path, '*'))
    else:
        return gb.glob(path+'*')

class STYLES:
    pass

class PersonalRagCLI(cmd.Cmd):
    prompt = 'PersonalRAG>> '
    intro = 'Welcome to PersonalRAG.\nType "help" for available commands.\nType "bye" to exit.'
    
    def __init__(self):
        super().__init__()
        self.current_directory = os.getcwd()
        # TODO: make the retriever be actually loaded if the relevant files exist
        self.retriever = Retriever(db_path="./data/database_files/retriever.db", index_path="./data/database_files/faiss.index")
        
        self.cache_dir = "./data"
        if not os.path.exists(self.cache_dir):
            os.makedirs(self.cache_dir)
    
    
    def do_load_my_data(self, dirpath):
        """
        Loads and preprocessed your pdfs to be ready to use with the RAG system. Requires a path to the folder with your pdfs
        For example:
            load_my_data ./documents/my_pdfs
        """
        
        path = Path(dirpath)
                
        if not path.is_dir():
            print(f"The provided path '{dirpath}' is not an existing directory.")
            return        
                
        preprocess_dir = f"{self.cache_dir}/processed"
        if not os.path.exists(preprocess_dir):
            os.makedirs(preprocess_dir)
        
        preprocess_pdfs_in_directory(dirpath, savepath=preprocess_dir)
        
        # ingest
        self.retriever = create_faiss_index(preprocess_dir)    
    
    def complete_load_my_data(self, text, line, start_idx, end_idx):
        return _complete_path(text)
    
    def query_result_pretty_print(self, results):
        docs = {}
        for res in results:
            title = res['header']['title']
            page = res['header']['page']
            if title in docs.keys():
                docs[title].append(page)
            else:
                docs[title] = [page]
        
        for filename, pages in docs.items():
            print(filename)
            print(f"\tRelevant pages : {sorted(pages)}")
    
    def do_query(self, query):
        """
        Allows you to ask a query to Retriever. It will retrieve document chunks with relevant text and give you the relevant pages in the pdf. 
        For example:
            query "How do I add 2+2?"
        """
        results = self.retriever.retrieve(query)
        print("\nWe found the following document chunks most relevant to your query:\n")
        self.query_result_pretty_print(results)
        
    def do_rag_query(self, query):
        chunks = self.retriever.retrieve(query)
        # prompt = self.retriever.get_prompt(chunks) TODO: figure out the design of this
        
    def postcmd(self, stop, line):
        print()  
        return stop
    
    def do_bye(self, args):
        """Exits the CLI."""
        print("\nGoodbye!")
        return True
    
if __name__ == '__main__':
    PersonalRagCLI().cmdloop()