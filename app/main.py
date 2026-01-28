import os
import streamlit as st
from dotenv import load_dotenv
from document_processor import DocumentProcessor
from vector_store import VectorStoreManager
from summarizer import CentralSummarizer
from llm_manager import AIChainManager

# Load environment variables
load_dotenv()

MODEL_NAME = os.getenv("SELECTED_MODEL", "llama3.2:1b")
OLLAMA_BASE_URL = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")
NOTES_DIR = os.getenv("NOTES_DIR", "./notes")
CHROMA_DIR = os.getenv("CHROMA_DIR", "./data/chroma")
INDEX_PATH = os.getenv("INDEX_PATH", "./data/central_index.json")

st.set_page_config(page_title="AI Notes Assistant", layout="wide")

st.title("📚 AI Interactive Notes Server")
st.sidebar.info(f"Model: {MODEL_NAME}")

# Initialize components
@st.cache_resource
def init_components():
    try:
        doc_processor = DocumentProcessor(NOTES_DIR)
        vector_store = VectorStoreManager(CHROMA_DIR)
        summarizer = CentralSummarizer(INDEX_PATH, MODEL_NAME, OLLAMA_BASE_URL)
        chain_manager = AIChainManager(MODEL_NAME, vector_store, summarizer, OLLAMA_BASE_URL)
        return doc_processor, vector_store, summarizer, chain_manager
    except Exception as e:
        st.error(f"Error initializing components: {e}")
        return None, None, None, None

doc_processor, vector_store, summarizer, chain_manager = init_components()

if not doc_processor:
    st.warning("Please make sure Ollama is running and the model is pulled.")
    st.stop()

# Sidebar for indexing
with st.sidebar:
    st.header("Note Management")
    if st.button("Sync & Re-index Notes"):
        with st.spinner("Processing notes..."):
            docs = doc_processor.load_documents()
            if not docs:
                st.info("No notes found to index.")
            else:
                split_docs = doc_processor.split_documents(docs)
                vector_store.add_documents(split_docs)
                summarizer.summarize_new_files(docs)
                st.success(f"Indexed {len(docs)} files successfully!")

# Chat Interface
if "messages" not in st.session_state:
    st.session_state.messages = []

for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

if prompt := st.chat_input("Ask a question about your notes..."):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):
        with st.spinner("Thinking..."):
            response = chain_manager.ask(prompt)
            st.markdown(response)

    st.session_state.messages.append({"role": "assistant", "content": response})
