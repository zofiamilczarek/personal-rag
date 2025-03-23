# Personal RAG

This repo is an implementation of a RAG pipeline made for personal use. It is currently still a work in progress, but you are welcome to check it out and use it! All feedback is welcome.

## Installation
1. Clone this repo
```
git clone https://github.com/zofiamilczarek/personal-rag.git
```
2. Create an environment and install the dependencies

You can create the environment in any way you like. Here's a conda example, but feel free to use venv, virtualenv, or anything else.
```
conda create -n personal_rag_env python=3.11
conda activate personal_rag_env
```
Make sure you are in the repo's directory and run this:
```
pip install .
```
It will install all the necessary libraries.

Congrats! You can now use your personal RAG to query your documents!

## Usage

To use the CLI do the following:

```
python src/personal_rag/cli.py
```
Which will start the app. You should get this:

```
Welcome to PersonalRAG. Type "help" for available commands.
PersonalRAG>>
```
1. Loading Files

You can use this command to load your personal pdf files:
```
PersonalRAG>> load_my_data path_to_my_pdfs
```

2. Querying the created database
```
PersonalRAG>> query "What is Word2Vec?"
```


