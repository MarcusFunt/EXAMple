import os
import pytest
from app.document_processor import DocumentProcessor
from app.summarizer import CentralSummarizer
from unittest.mock import MagicMock, patch

def test_document_processor_categorization(tmp_path):
    # Setup mock notes directory
    notes_dir = tmp_path / "notes"
    gen_dir = notes_dir / "general"
    gen_dir.mkdir(parents=True)
    test_file = gen_dir / "test.txt"
    test_file.write_text("This is a test note about grammar.")

    processor = DocumentProcessor(str(notes_dir))
    docs = processor.load_documents()

    assert len(docs) == 1
    assert docs[0].metadata['category'] == "general"
    assert "grammar" in docs[0].page_content

def test_hardware_detection_script():
    # Run the script and check .env
    import subprocess
    result = subprocess.run(["./scripts/detect_hardware.sh"], capture_output=True, text=True)
    assert result.returncode == 0
    assert os.path.exists(".env")
    with open(".env", "r") as f:
        content = f.read()
        assert "SELECTED_MODEL" in content

def test_summarizer_logic(tmp_path):
    index_path = tmp_path / "index.json"

    with patch('app.summarizer.OllamaLLM') as mock_ollama:
        summarizer = CentralSummarizer(str(index_path), "dummy-model")

        from langchain_core.documents import Document
        test_docs = [
            Document(page_content="Content of note", metadata={"source": "note.txt", "category": "test"})
        ]

        with patch('langchain_core.prompts.PromptTemplate.__or__') as mock_or:
            mock_chain = MagicMock()
            mock_chain.invoke.return_value = "This is a summary."
            mock_or.return_value = mock_chain

            summarizer.summarize_new_files(test_docs)

    assert "note.txt" in summarizer.summaries
    assert summarizer.summaries["note.txt"]["summary"] == "This is a summary."
