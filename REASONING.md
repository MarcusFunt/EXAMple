# Reasoning and Architecture Decisions

This document outlines why certain choices were made during the development of the AI Notes Server.

## Hardware Detection Strategy
**Choice**: Detect hardware on the host via a bash script before starting Docker.
**Reasoning**: Detecting GPU VRAM and driver status reliably inside a Docker container can be complex and depends on the container being started with the correct flags. By scanning on the host first, we can dynamically generate a `.env` file that ensures the correct `docker-compose` configuration and model pull, leading to a smoother "single script" install experience.

## Model Selection (Llama-focused)
**Choice**: Use `llama3.2` for lower tiers and `llama3.1` for higher tiers.
**Reasoning**: `llama3.2:1b` and `3b` are exceptionally efficient for CPU-bound or low-memory systems, providing a usable experience where older models might struggle. `llama3.1:8b` and `70b` are state-of-the-art for mid-to-high end hardware, offering the "most powerful" experience requested.

## Central Index Summarization
**Choice**: Implementing a separate summarization step for each file.
**Reasoning**: Pure vector search (RAG) can sometimes lose the "big picture" of a document if relevant chunks are scattered or if the query is high-level (e.g., "What notes do I have on English grammar?"). By summarizing each file and providing a central index in the prompt, the AI has a "map" of the available knowledge, significantly improving its ability to find relevant context or summarize overall progress.

## Vector Store (ChromaDB)
**Choice**: ChromaDB.
**Reasoning**: It is lightweight, persists to disk easily, and integrates seamlessly with LangChain. It doesn't require a separate database server, keeping the Docker setup simple.

## UI (Vite + React)
**Choice**: Vite + React.
**Reasoning**: A lightweight React frontend provides a responsive chat UI, while a FastAPI backend serves APIs and static assets without Streamlit-specific constraints.

## Embeddings (HuggingFace)
**Choice**: `all-MiniLM-L6-v2` via HuggingFaceEmbeddings.
**Reasoning**: Running embeddings via Ollama requires pulling an additional model (like `nomic-embed-text`) and ensures the Ollama server is responsive during indexing. Using `sentence-transformers` locally in the app container is faster, more reliable, and reduces the complexity of the installation script.
