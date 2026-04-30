import os

from dotenv import find_dotenv, load_dotenv

load_dotenv(find_dotenv())

_OPENAI_KEY = os.getenv("OPENAI_API_KEY", "")
_OPENAI_MODELS = {"gpt-4.1", "gpt-4.1-mini", "gpt-4.1-nano", "gpt-4o", "gpt-4o-mini"}

# Model used when callers pass model=None.  Override with LLM_MODEL env var.
DEFAULT_MODEL: str = os.getenv("LLM_MODEL", "gpt-4.1-mini")


def get_api_key(provider: str, env_file: dict | None = None) -> str:
    """Return the API key for *provider*.  Kept for call_embedding.py compatibility."""
    if env_file is None:
        env_file = os.environ
    match provider:
        case "openai":
            return env_file["OPENAI_API_KEY"]
    raise ValueError(f"Unknown provider: {provider}")


def _use_ollama() -> bool:
    """True when no OpenAI key is configured → fall back to local Ollama."""
    return not _OPENAI_KEY or _OPENAI_KEY.lower() == "disabled"


def get_llm(model: str | None = None, temperature: float = 0.0, api_key: str | None = None):
    """Return a LangChain chat model.

    Falls back to Ollama automatically when OPENAI_API_KEY is empty or "disabled".
    Override the default model via the LLM_MODEL environment variable.
    """
    if model is None:
        model = DEFAULT_MODEL

    if _use_ollama():
        from langchain_ollama import ChatOllama
        # If LLM_MODEL is an OpenAI name, substitute the Ollama default instead.
        ollama_model = os.getenv(
            "OLLAMA_MODEL",
            model if model not in _OPENAI_MODELS else "llama3.2",
        )
        base_url = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")
        return ChatOllama(model=ollama_model, temperature=temperature, base_url=base_url)

    if model in _OPENAI_MODELS:
        from langchain_openai import ChatOpenAI
        key = api_key or _OPENAI_KEY
        return ChatOpenAI(model_name=model, temperature=temperature, openai_api_key=key)

    raise ValueError(f"Unknown model: {model!r}. Set LLM_MODEL to a supported value.")
