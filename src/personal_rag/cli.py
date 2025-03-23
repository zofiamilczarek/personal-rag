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
        # TODO: make the retriever be actually loaded if the relevant files exist
        self.retriever = Retriever(db_path="./data/database_files/retriever.db", index_path="./data/database_files/faiss.index")
    
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
    
    def do_load_my_data(self, dirpath):
        """
        Loads and preprocessed your pdfs to be ready to use with the RAG system. Requires a path to the folder with your pdfs
        For example:
            load_my_data ./documents/my_pdfs
        """
        
        path = Path(dirpath)
                
        # TODO: WEEWOOWEEWOO this throws an error when it shouldnt
        if not path.is_dir():
            print("The provided path '{dirpath}' is not an existing directory.")
            return        
                
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
        self.retriever = create_faiss_index("./data/processed")
            
    
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
        pass
    
    def postcmd(self, stop, line):
        print()  # Add an empty line for better readability
        return stop
    
    
if __name__ == '__main__':
    PersonalRagCLI().cmdloop()