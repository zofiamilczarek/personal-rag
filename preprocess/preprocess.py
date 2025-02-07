# parses the pdfs
# manages the vector database
import PyPDF2

def extract_pdf_text_page_numbers(pdf_path : str) -> list[str]:
    """Returns a list of strings, eahc representing a page of the pdf document from `pdf_path`"""
    # Open the PDF file in binary mode
    with open(pdf_path, 'rb') as file:
        reader = PyPDF2.PdfReader(file)
        extracted_data = {}

        # Loop over each page in the PDF
        for page_number, page in enumerate(reader.pages, start=1):
            text = page.extract_text()
            # Store the text along with its page number
            extracted_data[page_number] = text

    return extracted_data


def do_chunk_page(page: str, page_nb: int, title: str, max_chunk_size: int, min_chunk_size: int = None) -> list[dict]:
    # TODO
    # decide how to chunk things
    #   - dumb way: just do each chunk of max_chunk_size and the last one is whatever is left
    #               problem : this can lead to chunks with just one word
    #   - smarter way: if the last chunk size too small (say, under 10% of max chunk size), then split it so that each chunk is at least min_chunk_size
    header = {"page" : page_nb, "title" : title}
    page = page.split(' ')
    # efficiently select slices of the page that constitute a chunk
    
    page_chunks = []
    for i in range(0, len(page), max_chunk_size):
        chunk = {'header' : header, 'chunk' : page[i:i + max_chunk_size]}
        page_chunks.append(chunk)        
    
    return page_chunks
    
    

if __name__ == '__main__':
    # pdf_path = "./documents/nlp_textbook_jurafsky.pdf"  # Replace with your PDF file path
    
    pdf_path = "./documents/Francuski_Raz_a_dobrze_ebook_LINGO.pdf"
    data = extract_pdf_text_page_numbers(pdf_path)
    
    # Example: Print the text of each page with its number
    for page, text in data.items():
        print(f"--- Page {page} ---")
        print(text)
        print("\n")
        
        if page == 10 : break
    

