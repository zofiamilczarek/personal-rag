import cmd
import os
import glob as gb
from personal_rag.rag import Retriever
from pathlib import Path
from personal_rag.preprocess import preprocess_pdfs_in_directory
import shutil
import sys

def rm_r(path):
    if os.path.isdir(path) and not os.path.islink(path):
        shutil.rmtree(path)
    elif os.path.exists(path):
        os.remove(path)
    else:
        print("Not a path TODO make this an exception")


import readline

readline.set_completer_delims(' \t\n')


if 'libedit' in readline.__doc__:
    readline.parse_and_bind("bind ^I rl_complete")
else:
    readline.parse_and_bind("tab: complete")


def _complete_path(path):
    """A method to handle path autocomplete in a cmd.Cmd interface"""
    if os.path.isdir(path):
        return gb.glob(os.path.join(path, '*'))
    else:
        return gb.glob(path+'*')

class _Wrapper:

    def __init__(self, fd):
        self.fd = fd

    def readline(self, *args):
        try:
            return self.fd.readline(*args)
        except KeyboardInterrupt:
            print("C ya")
            return '\n'

class PersonalRagCLI(cmd.Cmd):
    prompt = 'PersonalRAG>> '
    intro = 'Welcome to PersonalRAG.\nType "help" for available commands.\nType "bye" to exit.'

    def __init__(self):

        print("Starting up ...")
        super().__init__(stdin=_Wrapper(sys.stdin))
        self.current_directory = os.getcwd()
        # TODO: make the retriever be actually loaded if the relevant files exist
        self.retriever = Retriever(db_path="./data/database_files/retriever.db", index_path="./data/database_files/faiss.index")

        self.cache_dir = "./data"
        if not os.path.exists(self.cache_dir):
            os.makedirs(self.cache_dir)



    def do_index(self, args):
        """
        Indexes data in case there was more?
        """

        preprocess_dir = f"{self.cache_dir}/processed"
        if not os.path.exists(preprocess_dir):
            print("Cannot find /processed directory")

        print("Indexing data ...")

        # ingest
        self.retriever.index_processed(preprocess_dir, clear_index=False)
        print("Done.")

    def do_load(self, dirpath):
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

        print("Starting preprocessing ...")

        preprocess_pdfs_in_directory(dirpath, savepath=preprocess_dir)

        print("Done.")

        print("Indexing data ...")

        # ingest
        self.retriever.index_processed(preprocess_dir)
        print("Done.")

    def complete_load(self, text, line, start_idx, end_idx):
        return _complete_path(text)

    def complete_query(self, text, line, start_idx, end_idx):
        return _complete_path(text)

    def do_clean(self, args):
        print("Nuking folders ...")
        rm_r("./data/database_files")
        rm_r("./data/processed")
        print("Done.")

        print("Restarting DB ... \n\n")
        self.retriever.db.__init__() # I hate this so much



    def __query_result_pretty_print(self, results):
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
        self.__query_result_pretty_print(results)

    def do_rag_query(self, query):
        """
        Allows you to ask a query to the RAG system. It will give you an answer to your question based on the retrieved document chunks.
        For example:
            rag_query "How do I add 2+2?"
        """
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
