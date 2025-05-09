import sys
import os

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from database.db_manager import create_vector_db, get_vector_db


def main():
    input_path = "./database/input_db"
    persist_path = "./database/vector_db"
    embedding_model = "openai"

    print(f"Checking input folder: {input_path}")
    if not os.path.exists(input_path):
        print(f"❌ Folder {input_path} not found.")
        return

    print("🔄 Creating vector database...")
    vector_db = create_vector_db(
        files=input_path,
        persist_dir=persist_path,
        embeddings=embedding_model
    )
    print("✅ Vector database created and persisted.")

    print("📦 Loading vector database for testing...")
    loaded_db = get_vector_db(
        file_path=input_path,
        persist_path=persist_path,
        embedding=embedding_model
    )

    print("🔍 Checking number of documents in vector DB...")
    print("Total documents stored:", len(loaded_db.get()['documents']))

if __name__ == '__main__':
    main()