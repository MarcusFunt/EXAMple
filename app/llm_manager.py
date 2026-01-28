from langchain_ollama import OllamaLLM
from langchain.chains import RetrievalQA
from langchain_core.prompts import PromptTemplate
from summarizer import CentralSummarizer
from vector_store import VectorStoreManager

class AIChainManager:
    def __init__(self, model_name: str, vector_store: VectorStoreManager, summarizer: CentralSummarizer, base_url: str = "http://localhost:11434"):
        self.model_name = model_name
        self.vector_store = vector_store
        self.summarizer = summarizer
        self.llm = OllamaLLM(model=model_name, base_url=base_url)

        template = """You are an AI assistant for a student's notes. Use the following pieces of context and the central index to answer the question at the end.
If you don't know the answer, just say that you don't know, don't try to make up an answer.

CENTRAL INDEX SUMMARY:
{central_index}

CONTEXT FROM NOTES:
{context}

QUESTION: {question}
HELPFUL ANSWER:"""

        self.prompt = PromptTemplate(
            template=template,
            input_variables=["context", "question", "central_index"]
        )

    def ask(self, query: str):
        # We manually build the chain to include the central index
        context_docs = self.vector_store.search(query)
        context_text = "\n\n".join([doc.page_content for doc in context_docs])
        central_index_text = self.summarizer.get_central_index_content()
        # Truncate central index if it's too long for the context window
        if len(central_index_text) > 8000:
            central_index_text = central_index_text[:8000] + "... [truncated]"

        full_prompt = self.prompt.format(
            context=context_text,
            central_index=central_index_text,
            question=query
        )

        return self.llm.invoke(full_prompt)
