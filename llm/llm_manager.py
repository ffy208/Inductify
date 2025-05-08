import os
import openai

from dotenv import find_dotenv
from langchain_openai import ChatOpenAI
from pipenv.utils.environment import load_dot_env


def get_api_key(provider:str, env_file:dict()=None):
    if env_file is None:
        load_dot_env(find_dotenv())
        env_file = os.environ
    match provider:
        case "openai":
            return env_file["OPENAI_API_KEY"]
        #TODO: add more

    raise ValueError(f"Invalid model: {provider}")

def get_llm(model:str=None, temperature:float=0.0, api_key:str=None):
    if model in ["gpt-4.1", "gpt-4.1-mini", "gpt-4.1-nano", "gpt-4o", "gpt-4o-mini"]:
        if api_key is None:
            api_key = get_api_key(model, os.environ)
        llm = ChatOpenAI(model_name = model, temperature = temperature , openai_api_key = api_key)
    #TODO: add more!
    else:
        raise ValueError(f"Invalid model: {model}")
    return llm

def get_chat_completion(prompt:str, model:str, temperature: float, api_key:str, max_tokens:int):
    if api_key is None:
        api_key = get_api_key("openai")
    openai.api_key = api_key
    messages = [{"role": "user", "content": prompt}]
    response = openai.ChatCompletion.create(
        model=model,
        message=messages,
        temperature=temperature,
        max_tokens=max_tokens,
    )
    return response.choices[0].message["content"]
