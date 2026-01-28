import os
import json
from typing import List, Dict
from langchain_core.documents import Document
from langchain_ollama import OllamaLLM
from langchain_core.prompts import PromptTemplate

class CentralSummarizer:
    def __init__(self, index_path: str, model_name: str, base_url: str = "http://localhost:11434"):
        self.index_path = index_path
        self.llm = OllamaLLM(model=model_name, base_url=base_url)
        self.summaries = self._load_index()

    def _load_index(self) -> Dict[str, str]:
        if os.path.exists(self.index_path):
            with open(self.index_path, 'r') as f:
                return json.load(f)
        return {}

    def _save_index(self):
        with open(self.index_path, 'w') as f:
            json.dump(self.summaries, f, indent=4)

    def summarize_new_files(self, documents: List[Document]):
        # Group documents by source
        grouped_docs = {}
        for doc in documents:
            source = doc.metadata['source']
            if source not in grouped_docs:
                grouped_docs[source] = []
            grouped_docs[source].append(doc.page_content)

        updated = False
        for source, contents in grouped_docs.items():
            if source not in self.summaries:
                print(f"Summarizing {source}...")
                full_text = "\n".join(contents)[:4000] # Limit text for summary
                prompt = PromptTemplate.from_template(
                    "Summarize the following notes concisely. Focus on the main subject and key points. "
                    "Category: {category}\n\nContent: {content}"
                )
                category = "Unknown"
                # Find category from a doc
                for doc in documents:
                    if doc.metadata['source'] == source:
                        category = doc.metadata['category']
                        break

                chain = prompt | self.llm
                summary = chain.invoke({"category": category, "content": full_text})
                self.summaries[source] = {
                    "summary": summary,
                    "category": category,
                    "filename": os.path.basename(source)
                }
                updated = True

        if updated:
            self._save_index()

    def get_central_index_content(self) -> str:
        content = "Central Index of Notes:\n"
        for source, data in self.summaries.items():
            content += f"- {data['filename']} ({data['category']}): {data['summary']}\n"
        return content
