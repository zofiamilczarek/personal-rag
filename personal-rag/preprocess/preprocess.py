# parses the pdfs into chunks
import os
import PyPDF2
import numpy as np
from typing import List, Dict
from tqdm import tqdm
import json

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


if __name__ == "__main__":
    pdf_path = "./data/raw_pdfs/nlp_textbook_jurafsky.pdf"
    
    chunks = get_pdf_chunks(pdf_path)
    with open('./data/processed/chunks.json', 'w') as f:
        f.write(json.dumps(chunks))
    
    print(*chunks[:10], sep="\n\n")
    