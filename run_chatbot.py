import gradio as gr
import json
import os
import base64
from datetime import datetime
import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from app.chatbot import generate_response, save_data

HISTORY_FILE = "data/chat_history.json"
LOGO_PATH = "assets/logo_small.png"
FAVICON_PATH = "assets/favicon.ico"


def image_to_base64(path):
    with open(path, "rb") as f:
        return base64.b64encode(f.read()).decode("utf-8")

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
    response = generate_response(message)
    history.append([message, response])
    save_history(history)
    return "", history

def clear_chat():
    if os.path.exists(HISTORY_FILE):
        os.remove(HISTORY_FILE)
    return "", []

# UI Launch
def build_interface():
    logo_base64 = image_to_base64(LOGO_PATH)

    with gr.Blocks(title="Ask NileEdge AI", head=f"<link rel='icon' type='image/x-icon' href='{FAVICON_PATH}'>") as demo:
        gr.HTML(f"""
        <style>
            body {{
                background-color: #121212;
                color: #e0e0e0;
                background-image: url('data:image/png;base64,{logo_base64}');
                background-repeat: no-repeat;
                background-position: center;
                background-size: 25%;
                opacity: 0.96;
            }}
            .gr-button {{ background-color: #1f6feb; color: white; }}
            .gr-button:hover {{ background-color: #388bff; }}
            .gr-textbox input, .gr-textbox textarea {{
                background-color: #1e1e1e;
                color: white;
            }}
            .loading-spinner {{
                display: inline-block;
                width: 24px;
                height: 24px;
                border: 3px solid rgba(255, 255, 255, 0.3);
                border-radius: 50%;
                border-top-color: #4fc3f7;
                animation: spin 1s ease-in-out infinite;
            }}
            .gr-chatbot-message.user {
                background-color: #1e1e1e;
                color: white;
            }
            .gr-chatbot-message.bot {
                background-color: #2e3b4e;
                color: #4fc3f7;
            }
            @keyframes spin {{
                to {{ transform: rotate(360deg); }}
            }}
        </style>
        """)

        gr.HTML(f"""
        <div style="text-align: center;">
            <img src="data:image/png;base64,{logo_base64}" width="90" style="margin-bottom: 10px;">
            <h1 style="color: #4fc3f7;">Ask NileEdge AI</h1>
            <p style="color: #b0bec5;">Your assistant powered by our website's knowledge.</p>
        </div>
        """)

        chatbot = gr.Chatbot(value=load_history())
        with gr.Row():
            msg = gr.Textbox(placeholder="Ask something about NileEdge...", scale=9)
            send_btn = gr.Button("Send", scale=1)

        loading = gr.HTML("", visible=True)

        def handle_submit(message, chat_history):
            chat_history = chat_history or []
            chat_history.append([message, None])
            
            yield "", chat_history, "<div class='loading-spinner'></div>"

            response = generate_response(message)
            chat_history[-1][1] = response
            save_history(chat_history)
            yield "", chat_history, ""

        send_btn.click(handle_submit, inputs=[msg, chatbot], outputs=[msg, chatbot, loading])
        msg.submit(handle_submit, inputs=[msg, chatbot], outputs=[msg, chatbot, loading])
        demo.load(fn=lambda: ("", load_history()), outputs=[msg, chatbot])

    return demo

if __name__ == "__main__":
    import atexit
    atexit.register(save_data)
    demo = build_interface()
    demo.launch(share=True)
