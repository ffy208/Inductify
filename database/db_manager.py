import os
import tempfile

from botocore import loaders
from langchain_community.document_loaders import PyMuPDFLoader, UnstructuredExcelLoader, UnstructuredMarkdownLoader, \
    UnstructuredFileLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from embedding.call_embedding import get_embedding
from langchain.vectorstores import Chroma


DEFAULT_DB_PATH = "./input_db"
DEFAULT_PERSIST_PATH = "./vector_db"
CHUNK_SIZE = 500
CHUNK_OVERLAP = 150

def get_file_list(dir_path):
    file_list = []
    for root, dirs, files in os.walk(dir_path):
        for file in files:
            file_list.append(os.path.join(root, file))
    return file_list

def file_loader(file, loaders):
    if isinstance(file, tempfile._TemporaryFileWrapper):
        file = file.name
    if not os.path.isfile(file):
        [file_loader(os.path.join(file,f), loaders) for f in os.listdir(file)]
        return
    file_type = file.split('.')[-1]
    match file_type:
        case 'pdf':
            loaders.append(PyMuPDFLoader(file))
        case 'xlsx':
            loaders.append(UnstructuredExcelLoader(file))
        case 'md':
            loaders.append(UnstructuredMarkdownLoader(file))
        case 'txt':
            loaders.append(UnstructuredFileLoader(file))
        #TODO: add more support types
    return

def create_db_info(files=DEFAULT_DB_PATH, embeddings = "openai", persist_dir = DEFAULT_PERSIST_PATH):
    if embeddings == "openai":
        vector_db = create_vector_db(files, persist_dir, embeddings)
    return vector_db

def create_vector_db(files=DEFAULT_DB_PATH, persist_dir = DEFAULT_PERSIST_PATH, embeddings = "openai"):
    if files == None:
        return "Please provide path to database"
    if type(files) != list:
        files = [files]
    loader = []
    [file_loader(file, loaders) for file in files]
    docs = []
    for loader in loaders:
        if loader != None:
            docs.extend(loader.load())

    text_splitter = (RecursiveCharacterTextSplitter(chunk_size=CHUNK_SIZE, chunk_overlap=CHUNK_OVERLAP))
    split_docs = text_splitter.split_documents(docs)
    if type(embeddings) == str:
        embeddings = get_embedding(embedding=embeddings)

    vector_db = Chroma.from_documents(documents=split_docs, embedding=embeddings, persist_dir=persist_dir)
    vector_db.persist()
    return vector_db



def load_input_db(path, embeddings):
    vector_db = Chroma(
        persist_directory=path,
        embedding_function=embeddings
    )
    return vector_db

def persist_input_db(vector_db):
    vector_db.persist()

def update_vector_db(vector_db, files, persist_dir, embeddings):
    #TODO: update vector database when admin user need add more files into app
    ...

def get_vector_db(file_path:str=None, persist_path:str=None, embedding="openai", embedding_key:str=None):
    embedding = get_embedding(embedding=embedding, embedding_key=embedding_key)
    if os.path.exists(persist_path):
        contents = os.listdir(persist_path)
        if len(contents) == 0:
            vector_db = create_vector_db(file_path, persist_path, embedding)
            vector_db = load_input_db(persist_path, embedding)
        else:
            vector_db = load_input_db(persist_path, embedding)
    else:
        vector_db = create_vector_db(file_path, persist_path, embedding)
        vector_db = load_input_db(persist_path, embedding)
    return vector_db




if __name__ == '__main__':
    create_vector_db(embeddings = "openai")








