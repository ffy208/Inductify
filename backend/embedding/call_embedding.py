from langchain_openai import OpenAIEmbeddings
from openai import OpenAI
from backend.llm.llm_manager import get_api_key


def get_embedding(embedding:str, embedding_key:str=None, env_file:str=None):
    match embedding:
        case "openai":
            return OpenAIEmbeddings(openai_api_key=embedding_key)

    raise ValueError(f"embedding {embedding} not supported")

def get_chat_completion(prompt:str, model:str, temperature: float, api_key:str, max_tokens:int):
    if api_key is None:
        api_key = get_api_key("openai")
    client = OpenAI(api_key=api_key)
    response = client.chat.completions.create(
        model=model,
        messages=[{"role": "user", "content": prompt}],
        temperature=temperature,
        max_tokens=max_tokens,
    )
    return response.choices[0].message.content
