import gradio as gr
import os, json, sys, pathlib
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from app.chatbot import generate_response, save_data

# ─────────────────────────────────────────────
# paths
# ─────────────────────────────────────────────
DATA_DIR     = pathlib.Path("data")
DATA_DIR.mkdir(exist_ok=True)                 # create once
HISTORY_FILE = DATA_DIR / "chat_history.json"

def load_history():
    if HISTORY_FILE.exists():
        return json.loads(HISTORY_FILE.read_text(encoding="utf-8"))
    return []

def clear_history():
    HISTORY_FILE.unlink(missing_ok=True)
    return []

def save_history(history):
    HISTORY_FILE.write_text(
        json.dumps(history, indent=2, ensure_ascii=False),
        encoding="utf-8",
    )

# ─────────────────────────────────────────────
# streaming chat wrapper
# ─────────────────────────────────────────────
def chat_wrapper(message, history):
    history = history or []

    history.append({"role": "user", "content": message})
    history.append({"role": "assistant", "content": ""})
    yield "", history

    for tok in generate_response(message, history):
        history[-1]["content"] += tok
        yield "", history

    save_history(history)

# ─────────────────────────────────────────────
# build UI
# ─────────────────────────────────────────────
def build_interface():
    with gr.Blocks(title="Ask NileEdge AI") as demo:
        gr.Markdown("## Ask NileEdge&nbsp;AI")

        chatbot = gr.Chatbot(
            value=load_history(),
            height=450,
            type="messages",            # silences deprecation warning
        )
        msg       = gr.Textbox(placeholder="Type your question…")
        with gr.Row():
            send_btn  = gr.Button("Send", variant="primary")
            clear_btn = gr.Button("Clear chat")

        # Works on Gradio 3.x and 4.x (streaming detected automatically)
        send_btn.click(chat_wrapper, [msg, chatbot], [msg, chatbot])
        msg.submit(chat_wrapper,     [msg, chatbot], [msg, chatbot])

        clear_btn.click(
            lambda: ("", clear_history()),
            None, [msg, chatbot], queue=False,
        )

    return demo

# ─────────────────────────────────────────────
if __name__ == "__main__":
    import atexit
    atexit.register(save_data)       # persist FAQ cache & chat log
    build_interface().launch(share=True)
