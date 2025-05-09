# Inductify

A smart onboarding assistant that helps new hires quickly access essential knowledge, ask questions, and ramp up efficiently using LLM-powered technology.

## Features

- LLM-powered Q&A for onboarding
- Knowledge base with vector search
- FastAPI backend and Next.js frontend
- Embedding and document management
- Modular, extensible codebase

## Project Structure

```
Inductify/
  backend/         # Python backend (FastAPI, DB, LLM, Embedding)
  TSfrontend/      # TypeScript frontend (Next.js, React) | Under construction👷
  app.py           # Frontend entry (Gradio)
```

## Getting Started

### Backend

1. Install dependencies:
   ```bash
   cd backend
   pip install -r requirements.txt
   ```
2. Run the backend server:
   ```bash
   uvicorn backend.main:app --reload
   ```

### Frontend (Gradio App)

1. Run the frontend:
   ```bash
   python app.py
   ```

```##

- **Backend:** Python, LangChain, ChromaDB, FastAPI, SQLite
- **Frontend:** Gradio
- **LLM/Embedding:** OpenAI

## Contribution

Pull requests are welcome! For major changes, please open an issue first to discuss what you would like to change.

## License

This project is licensed under the MIT License.
```
