# parses the pdfs
# manages the vector database
import os
import PyPDF2
import numpy as np
from typing import List, Dict
from tqdm import tqdm

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
        for page_number, page in tqdm(enumerate(reader.pages)):
            extracted_data[page_number + 1] = page.extract_text()
    return extracted_data

def chunk_text(page: str, page_nb: int, title: str, max_chunk_size: int) -> List[Dict]:
    """Chunks a page into smaller parts, preserving metadata."""
    header = {"page": page_nb, "title": title}
    words = page.split()
    return [{"header": header, "chunk": " ".join(words[i:i + max_chunk_size])} for i in range(0, len(words), max_chunk_size)]

if __name__ == "__main__":
    # pdf_path = "./documents/nlp_textbook_jurafsky.pdf"  # Replace with your PDF file path
    
    pdf_path = "./documents/Francuski_Raz_a_dobrze_ebook_LINGO.pdf"
    data = extract_pdf_text_page_numbers(pdf_path)
    
    # Example: Print the text of each page with its number
    for page, text in data.items():
        print(f"--- Page {page} ---")
        print(text)
        print("\n")
        
        if page == 10 : break
    