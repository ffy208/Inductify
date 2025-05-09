import pytest
from unittest.mock import patch, MagicMock
import database.db_manager as dbm
import fitz  # pymupdf

def test_get_file_list(tmp_path):
    file1 = tmp_path / 'a.txt'
    file1.write_text('test')
    file2 = tmp_path / 'b.txt'
    file2.write_text('test')
    files = dbm.get_file_list(str(tmp_path))
    assert len(files) == 2
    assert str(file1) in files and str(file2) in files

@patch('database.db_manager.PyMuPDFLoader')
def test_file_loader_pdf(mock_loader, tmp_path):
    file = tmp_path / 'a.pdf'
    file.write_text('test')
    loaders = []
    dbm.file_loader(str(file), loaders)
    assert mock_loader.called

@patch('database.db_manager.get_embedding')
@patch('database.db_manager.Chroma')
@patch('database.db_manager.RecursiveCharacterTextSplitter')
def test_create_vector_db(mock_splitter, mock_chroma, mock_get_embedding, tmp_path):
    mock_get_embedding.return_value = MagicMock()
    mock_splitter.return_value.split_documents.return_value = ['doc1', 'doc2']
    mock_chroma.from_documents.return_value = MagicMock(persist=lambda: None)
    path = str(tmp_path / 'a.pdf')
    doc = fitz.open()
    page = doc.new_page()
    page.insert_text((72, 72), "This is a test PDF")
    doc.save(path)
    doc.close()
    result = dbm.create_vector_db(files=[path], persist_dir=str(tmp_path), embeddings='openai')
    assert mock_chroma.from_documents.called

@patch('database.db_manager.Chroma')
def test_load_input_db(mock_chroma):
    mock_chroma.return_value = 'mocked_db'
    result = dbm.load_input_db('path', 'embeddings')
    assert result == 'mocked_db'
