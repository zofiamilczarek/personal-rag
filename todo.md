### What I want :
- preprocess pdfs into chunks ready for the retriever
- do it in such a way that adding new docs doesnt mean recomputing everything for all documents
- each chunk should have a head that includes
    - the document's title
    - the document's page
    - (\*) a subtitle

!!!!!!

- implement tests. NO DO IT REALLY

!!!!!!

### current problems:
- there can be duplicates. I need to add a way to handle them
    - checking with a hash set
    - maybe some dumb solution. Since you would be loading it file by file, you can keep a list of 'loaded' files. If a file doesm't appear on that list you don't load it. It would be implemented in the data ingestion script
- 




chat's project structure advice:

rag_project/
│── data/                # Store PDFs and processed text chunks
│   ├── raw_pdfs/        # Original PDFs
│   ├── processed/       # Extracted text chunks
│── database/            # Database-related code
│   ├── database.py      # SQLite database handling
│   ├── retriever.db     # The actual SQLite database file (ignored in version control)
│── retriever/           # Retrieval logic
│   ├── retriever.py     # FAISS and document retrieval
│   ├── faiss.index      # FAISS index file (ignored in version control)
│── scripts/             # Utility scripts
│   ├── preprocess.py    # Extracts text from PDFs and prepares chunks
│   ├── ingest.py        # Loads extracted chunks into the database
│── models/              # Stores ML models (optional)
│   ├── sentence_transformer/  # Pretrained models for embeddings
│── notebooks/           # Jupyter notebooks for experimentation
│── tests/               # Unit tests
│── config.py            # Configuration file for paths and parameters
│── requirements.txt     # Python dependencies
│── main.py              # Entry point for running the retriever
│── README.md            # Documentation
│── .gitignore           # Ignore database, FAISS index, and large files