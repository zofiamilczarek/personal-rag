# parses the pdfs into chunks
import os
import PyPDF2
import numpy as np
from typing import List, Dict
from tqdm import tqdm
import json
import argparse
from pathlib import Path
from personal_rag.preprocess import get_pdf_chunks


def main():
    parser = argparse.ArgumentParser(
        prog = "Data Preprocessing script",
        description="Preprocesses the pdfs in the given directory into chunks",
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
            
main()