# Quick Demo Frontend
import uuid
import gradio as gr
import requests

session_id = str(uuid.uuid4())

def ask(message, history):
    payload = {
        "session_id": session_id,
        "message": message
    }
    r = requests.post("http://127.0.0.1:8000/ask", json=payload)
    print("Raw response from backend:", r.text)
    return r.json().get("answer","Error")

gr.ChatInterface(
    fn=ask,
    type="messages"
).launch()