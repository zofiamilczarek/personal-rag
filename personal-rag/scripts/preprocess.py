# parses the pdfs into chunks
import os
import PyPDF2
import numpy as np
from typing import List, Dict
from tqdm import tqdm
import json
import argparse
from pathlib import Path

def load_pdfs_from_directory(directory: str) -> Dict[str, Dict[int, str]]:
    """Loads all PDFs from a given directory and extracts text from each page."""
    pdf_texts = {}
    for filename in os.listdir(directory):
        if filename.endswith(".pdf"):
            pdf_path = os.path.join(directory, filename)
            pdf_texts[filename] = extract_pdf_text_page_numbers(pdf_path)
    return pdf_texts

def extract_pdf_text_page_numbers(pdf_path: str) -> Dict[int, str]:
    """Extracts text from a PDF and returns a dictionary mapping page numbers to text."""
    with open(pdf_path, 'rb') as file:
        reader = PyPDF2.PdfReader(file)
        extracted_data = {}
        for page_number, page in tqdm(enumerate(reader.pages), desc=f"Extracting file {pdf_path}"):
            extracted_data[page_number + 1] = page.extract_text()
    return extracted_data

def chunk_text(page: str, page_nb: int, title: str, max_chunk_size: int) -> List[Dict]:
    """Chunks a page into smaller parts, preserving metadata."""
    header = {"page": page_nb, "title": title}
    words = page.split()
    return [{"header": header, "chunk": " ".join(words[i:i + max_chunk_size])} for i in range(0, len(words), max_chunk_size)]

def get_pdf_chunks(pdf_path: str, max_chunk_size: int = 500):
    pages = extract_pdf_text_page_numbers(pdf_path)
    all_chunks = []
    for page_nb, page_content in pages.items():
        page_chunks = chunk_text(page_content, page_nb, pdf_path, max_chunk_size)
        all_chunks.extend(page_chunks)
    return all_chunks



parser = argparse.ArgumentParser(
    prog = "Data Preprocessing script",
    description="Preprocesses the pdfs in the given directory into chunks",
    epilog=""
)

parser.add_argument("path", type=str, help="The path to the preprocessed file (or folder if calling with --batched)")
parser.add_argument("--batched", help="Wether to process a batch of files or one file.", action="store_true")


args = parser.parse_args()

path = Path(args.path)


if args.batched : 
    if not path.is_dir():
        raise NotADirectoryError(f"The provided path '{args.path}' is not a directory.")
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
            print(f"")
else: 
    chunks = get_pdf_chunks(args.path)
    file_name = path.stem
    with open(f'./data/processed/{file_name}_chunks.json', 'w') as f:
        f.write(json.dumps(chunks)) 