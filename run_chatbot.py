import gradio as gr
import os
import json
import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from app.chatbot import generate_response, save_data

HISTORY_FILE = "data/chat_history.json"

def load_history():
    if os.path.exists(HISTORY_FILE):
        with open(HISTORY_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    return []

def save_history(history):
    with open(HISTORY_FILE, "w", encoding="utf-8") as f:
        json.dump(history, f, indent=2, ensure_ascii=False)

def chat_wrapper(message, history):
    history = history or []
    response = generate_response(message, history)
    history.append([message, response])
    save_history(history)
    return "", history

def build_interface():
    with gr.Blocks(title="Ask NileEdge AI") as demo:
        gr.Markdown("## Ask NileEdge AI")
        chatbot = gr.Chatbot(value=load_history())
        msg = gr.Textbox(placeholder="Type your question...")
        send_btn = gr.Button("Send")

        send_btn.click(chat_wrapper, inputs=[msg, chatbot], outputs=[msg, chatbot])
        msg.submit(chat_wrapper, inputs=[msg, chatbot], outputs=[msg, chatbot])

    return demo

if __name__ == "__main__":
    import atexit
    atexit.register(save_data)
    demo = build_interface()
    demo.launch(share=True)
