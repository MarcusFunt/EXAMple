# Instructions for AI Agents

Welcome, Agent! This project is structured as a LangChain RAG application. Here are the key components and conventions:

## Project Structure

- `app/`: Contains the Python source code for the AI logic and UI.
  - `main.py`: Streamlit entry point.
  - `document_processor.py`: Handles file loading and splitting.
  - `vector_store.py`: Manages ChromaDB and HuggingFace Embeddings.
  - `summarizer.py`: Logic for the "Central Index" summarization.
  - `llm_manager.py`: Orchestrates the LLM chain.
- `scripts/`: Contains utility scripts like `detect_hardware.sh`.
- `notes/`: Directory where users place their notes in categorized subfolders.
- `data/`: Persistent storage for ChromaDB and the central index JSON.

## Key Logic

### Hardware Detection
The `scripts/detect_hardware.sh` is the source of truth for model selection. If you update model tiers, do it there.

### Central Index
Unlike standard RAG, this app maintains a `data/central_index.json` containing summaries of every file. This is injected into the prompt context to help the LLM understand the overall scope of the notes, even if the specific chunks aren't in the top-k vector results.

### Categorization
File categories are derived from folder names. Maintain this metadata in `metadata['category']` during document processing.

## Development Guidelines

- Always use `langchain_core` for core components (Documents, Prompts).
- When adding new file loaders, ensure they add the `category`, `source`, and `filename` metadata.
- If you modify the `AIChainManager`, ensure it still incorporates the `CENTRAL INDEX SUMMARY` into the prompt.
