import pytest
from embedding.call_embedding import get_embedding

def test_get_embedding_openai():
    embedding = get_embedding('openai')
    assert embedding is not None
    # Optionally check class name
    assert 'OpenAIEmbeddings' in str(type(embedding))

def test_get_embedding_invalid():
    with pytest.raises(ValueError):
        get_embedding('invalid_provider') 