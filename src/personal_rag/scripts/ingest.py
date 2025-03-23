import sys
import os
import argparse
from personal_rag.preprocess import create_faiss_index

def get_args():
    
    parser = argparse.ArgumentParser()
    
    parser.add_argument(
        "-p",
        "--path",
        type = str,
        default="./data/processed",
        help = "The path to the folder containing the preprocessed pdf files in json format to be used in the RAG pipeline",
    )
    
    parser.add_argument(
        "--clear-index",
        action="store_true",
        help="If set, the existing FAISS index will be cleared before indexing the documents."
    )
    
    parser.add_argument(
        "--preprocess",
        action="store_true",
        help="If set, the script will first preprocess the pdf files"
    )
    
    return parser.parse_args()

def main():
    args = get_args()
    create_faiss_index(args.path, args.clear_index)

main()