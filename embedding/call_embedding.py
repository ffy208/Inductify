from langchain_openai import OpenAIEmbeddings


def get_embedding(embedding:str, embedding_key:str=None, env_file:str=None):
    match embedding:
        case "openai":
            return OpenAIEmbeddings(openai_api_key=embedding_key)

    raise ValueError(f"embedding {embedding} not supported")
