import os
from langchain_community.vectorstores import Chroma
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_core.documents import Document
from typing import List

class VectorStoreManager:
    def __init__(self, persist_directory: str):
        self.persist_directory = persist_directory
        self.embeddings = HuggingFaceEmbeddings(model_name="all-MiniLM-L6-v2")
        self.vector_store = Chroma(
            persist_directory=persist_directory,
            embedding_function=self.embeddings
        )

    def add_documents(self, documents: List[Document]):
        # Deduplicate by removing existing documents with the same source
        sources = list(set([doc.metadata.get('source') for doc in documents if 'source' in doc.metadata]))
        for source in sources:
            try:
                self.vector_store.delete(where={"source": source})
            except Exception:
                # Source might not exist yet, which is fine
                pass

        if documents:
            self.vector_store.add_documents(documents)

    def search(self, query: str, k: int = 4):
        return self.vector_store.similarity_search(query, k=k)

    def get_retriever(self):
        return self.vector_store.as_retriever()
