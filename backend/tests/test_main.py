import pytest
from unittest.mock import patch
from httpx import AsyncClient
import httpx
from backend.app import app

@pytest.mark.asyncio
@patch("backend.app.get_chat_completion")
@patch("backend.app.vector_db")
async def test_ask_question(mock_vector_db, mock_get_chat_completion):
    # Mock the similarity_search method to return fake documents
    mock_vector_db.similarity_search.return_value = [
        type("MockDocument", (), {"page_content": "This is a test document."})()
    ]

    # Mock the LLM response
    mock_get_chat_completion.return_value = "This is a mocked answer."

    async with AsyncClient(
        transport=httpx.ASGITransport(app=app), base_url="http://test"
    ) as ac:
        response = await ac.post("/ask", json={"question": "What is this project about?"})

    assert response.status_code == 200
    data = response.json()
    assert "answer" in data
    assert data["answer"] == "This is a mocked answer."
