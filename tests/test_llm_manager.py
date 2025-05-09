import pytest
from unittest.mock import patch, MagicMock
from llm.llm_manager import get_api_key, get_llm, get_chat_completion

@patch('llm.llm_manager.load_dot_env')
def test_get_api_key_openai(mock_load_dot_env):
    env = {'OPENAI_API_KEY': 'test-key'}
    key = get_api_key('openai', env)
    assert key == 'test-key'

def test_get_api_key_invalid():
    with pytest.raises(ValueError):
        get_api_key('invalid', {'OPENAI_API_KEY': 'test-key'})

@patch('llm.llm_manager.ChatOpenAI')
def test_get_llm_openai(mock_chat_openai):
    mock_chat_openai.return_value = 'mocked_llm'
    llm = get_llm(model='gpt-4.1-mini', temperature=0.5, api_key='test-key')
    assert llm == 'mocked_llm'

def test_get_llm_invalid():
    with pytest.raises(ValueError):
        get_llm(model='invalid-model')

@patch('llm.llm_manager.openai.ChatCompletion.create')
def test_get_chat_completion(mock_create):
    mock_create.return_value = MagicMock(choices=[MagicMock(message={'content': 'response'})])
    result = get_chat_completion('prompt', 'gpt-4.1-mini', 0.5, 'test-key', 10)
    assert result == 'response' 