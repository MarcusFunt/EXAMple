# AI Interactive Notes Server

This project is a locally hosted AI assistant designed to help students interact with their notes. It uses LangChain for Retrieval Augmented Generation (RAG) and Ollama for running powerful LLMs locally. It automatically detects your hardware (CPU, RAM, GPU) to choose the best model tier for your system.

## Features

- **Hardware-Aware Model Selection**: Automatically chooses between 5 tiers of Llama models based on available RAM and VRAM.
- **Categorized Search**: Handles notes sorted by subject and type (General, Templates, Examples, Teacher-provided).
- **Central Index Summarization**: Automatically generates summaries of new files to provide high-level context during Q&A.
- **Dockerized**: Easy deployment with Docker and Docker Compose.
- **Web UI**: User-friendly chat interface built with Streamlit.
- **Multiformat Support**: Supports Markdown (.md), PDF, and Text (.txt) files.

## Prerequisites

- **Docker** and **Docker Compose** installed.
- **NVIDIA Container Toolkit** (if you have an NVIDIA GPU and want acceleration).
- **WSL2** (if running on Windows).

## Installation

1. **Clone the repository**:
   ```bash
   git clone <repository-url>
   cd <repository-name>
   ```

2. **Run the Install Script**:
   ```bash
   chmod +x install.sh
   ./install.sh
   ```
   The script will:
   - Scan your hardware.
   - Generate a `.env` file with the best model for your system.
   - Start the Docker containers (Ollama and the Web App).
   - Pull the selected model automatically.

3. **Add Your Notes**:
   Place your files in the `notes/` directory. You can use the following structure:
   - `notes/general/`: General information.
   - `notes/templates/`: Template files.
   - `notes/examples/`: Completed examples.
   - `notes/teacher_provided/`: Official materials.

4. **Access the Web Interface**:
   Open your browser and go to `http://localhost:8501`.

## Usage

- **Ask Questions**: Type your questions in the chat box to find information across all your notes.
- **Sync Notes**: Click the "Sync & Re-index Notes" button in the sidebar whenever you add or modify notes. This updates the vector store and the central index summaries.

## Model Tiers

- **Stage 1 (Low End)**: `llama3.2:1b` (optimized for low RAM/CPU)
- **Stage 2 (CPU + 16GB RAM)**: `llama3.2:3b`
- **Stage 3 (GPU 8-12GB VRAM)**: `llama3.1:8b`
- **Stage 4 (GPU 12-32GB VRAM)**: `llama3.1:8b` (Full precision)
- **Stage 5 (GPU 32GB+ VRAM)**: `llama3.1:70b`
