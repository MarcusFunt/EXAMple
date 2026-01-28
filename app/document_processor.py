import os
from typing import List
from langchain_community.document_loaders import TextLoader, PyPDFLoader, UnstructuredMarkdownLoader
from langchain_core.documents import Document
from langchain_text_splitters import RecursiveCharacterTextSplitter

class DocumentProcessor:
    def __init__(self, notes_dir: str):
        self.notes_dir = notes_dir
        self.text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=100)

    def load_documents(self) -> List[Document]:
        documents = []
        for root, dirs, files in os.walk(self.notes_dir):
            category = os.path.basename(root)
            if category == os.path.basename(self.notes_dir):
                category = "Uncategorized"

            for file in files:
                if file.startswith('.'):
                    continue

                file_path = os.path.join(root, file)
                try:
                    if file.endswith('.md'):
                        loader = UnstructuredMarkdownLoader(file_path)
                    elif file.endswith('.pdf'):
                        loader = PyPDFLoader(file_path)
                    elif file.endswith('.txt'):
                        loader = TextLoader(file_path)
                    else:
                        continue

                    docs = loader.load()
                    for doc in docs:
                        doc.metadata['category'] = category
                        doc.metadata['source'] = file_path
                        doc.metadata['filename'] = file
                    documents.extend(docs)
                except Exception as e:
                    print(f"Error loading {file_path}: {e}")

        return documents

    def split_documents(self, documents: List[Document]) -> List[Document]:
        return self.text_splitter.split_documents(documents)
