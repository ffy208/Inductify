import os
import tempfile
from langchain_community.document_loaders import PyMuPDFLoader, UnstructuredExcelLoader, UnstructuredMarkdownLoader, \
    UnstructuredFileLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_chroma import Chroma
from dotenv import load_dotenv

from backend.embedding.call_embedding import get_embedding

load_dotenv()

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DEFAULT_DB_PATH = os.path.join(BASE_DIR, "input_db")
DEFAULT_PERSIST_PATH = os.path.join(BASE_DIR, "vector_db")

CHUNK_SIZE = 500
CHUNK_OVERLAP = 150

class DatabaseManager:
    _instance = None
    def __new__(cls, *args, **kwargs):
        if not cls._instance:
            cls._instance = super(DatabaseManager, cls).__new__(cls)
        return cls._instance

    def __init__(self,
                file_path = DEFAULT_DB_PATH,
                persist_path = DEFAULT_PERSIST_PATH,
                embedding = "openai",
                embedding_key = None):
        self.file_path = file_path
        self.persist_path = persist_path
        self.embedding = get_embedding(embedding)
        self.vector_db = None
        self.load_or_create_vector_db()

    def load_or_create_vector_db(self):
        if not os.path.exists(self.persist_path):
            os.makedirs(self.persist_path)

        if os.path.exists(self.file_path) and os.listdir(self.persist_path):
            # 从已有的数据库加载，不需要 persist
            self.vector_db = Chroma(persist_directory=self.persist_path, embedding_function=self.embedding)
        else:
            # 从文档创建新数据库，需要 persist
            self.vector_db = self._create_vector_db()
            self.vector_db.persist()

    def _create_vector_db(self):
        files = [self.file_path] if isinstance(self.file_path, str) else self.file_path
        loaders = []
        for file in files:
            self._load_file(file, loaders)
        docs = []
        for loader in loaders:
            if loader:
                docs.extend(loader.load())

        text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=CHUNK_SIZE, chunk_overlap=CHUNK_OVERLAP)
        split_docs = text_splitter.split_documents(docs)

        return Chroma.from_documents(
            documents=split_docs,
            embedding=self.embedding,
            persist_directory=self.persist_path
        )

    def _load_file(self, file, loaders):
        if isinstance(file, tempfile._TemporaryFileWrapper):
            file = file.name
        if not os.path.isfile(file):
            for f in os.listdir(file):
                self._load_file(os.path.join(file, f), loaders)
            return
        file_type = file.split('.')[-1].lower()
        match file_type:
            case 'pdf':
                loaders.append(PyMuPDFLoader(file))
            case 'xlsx':
                loaders.append(UnstructuredExcelLoader(file))
            case 'md':
                loaders.append(UnstructuredMarkdownLoader(file))
            case 'txt':
                loaders.append(UnstructuredFileLoader(file))
            case _:
                pass

    def persist(self):
        self.vector_db.persist()

    def get_db(self):
        return self.vector_db

    def update_db(self, new_files):
        # TODO: Add logic for incremental updates
        raise NotImplementedError("Update logic not implemented yet.")

if __name__ == '__main__':
    manager = DatabaseManager()
    db = manager.get_db()




# def get_file_list(dir_path):
#     file_list = []
#     for root, dirs, files in os.walk(dir_path):
#         for file in files:
#             file_list.append(os.path.join(root, file))
#     return file_list


# def create_db_info(files=DEFAULT_DB_PATH, embeddings = "openai", persist_dir = DEFAULT_PERSIST_PATH):
#     if embeddings == "openai":
#         vector_db = create_vector_db(files, persist_dir, embeddings)
#     return vector_db

# def create_vector_db(files=DEFAULT_DB_PATH, persist_dir = DEFAULT_PERSIST_PATH, embeddings = "openai"):
#     if files == None:
#         return "Please provide path to database"
#     if type(files) != list:
#         files = [files]
#     loaders = []
#     [file_loader(file, loaders) for file in files]
#     docs = []
#     for loader in loaders:
#         if loader != None:
#             docs.extend(loader.load())
#
#     text_splitter = (RecursiveCharacterTextSplitter(chunk_size=CHUNK_SIZE, chunk_overlap=CHUNK_OVERLAP))
#     split_docs = text_splitter.split_documents(docs)
#     if type(embeddings) == str:
#         embeddings = get_embedding(embedding=embeddings)
#
#     vector_db = Chroma.from_documents(documents=split_docs, embedding=embeddings, persist_directory=persist_dir)
#     vector_db.persist()
#     return vector_db


#
# def load_input_db(path, embeddings):
#     vector_db = Chroma(
#         persist_directory=path,
#         embedding_function=embeddings
#     )
#     return vector_db


# def get_vector_db(file_path:str=None, persist_path:str=None, embedding="openai", embedding_key:str=None):
#     embedding = get_embedding(embedding=embedding, embedding_key=embedding_key)
#     if os.path.exists(persist_path):
#         contents = os.listdir(persist_path)
#         if len(contents) == 0:
#             vector_db = create_vector_db(file_path, persist_path, embedding)
#             vector_db = load_input_db(persist_path, embedding)
#         else:
#             vector_db = load_input_db(persist_path, embedding)
#     else:
#         vector_db = create_vector_db(file_path, persist_path, embedding)
#         vector_db = load_input_db(persist_path, embedding)
#     return vector_db
#


#
# if __name__ == '__main__':
#     create_vector_db(embeddings = "openai")





