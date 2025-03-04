import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from database import Database
from rag import Retriever

def main():
    """
    1. parse agrs
        a. should have an option to wipe the database clean and repopulate it
    2. load the pdf chunks
    3. create a retriever
    3. ingest all the chunks into the retriever
    """
    
    
main()