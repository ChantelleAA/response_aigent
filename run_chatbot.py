import gradio as gr
import os, json, sys, pathlib, time
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from app.chatbot import generate_response, save_data

# ─────────────────────────────────────────────
# paths
# ─────────────────────────────────────────────
PROJECT_ROOT = pathlib.Path(__file__).resolve().parent  
DATA_DIR = PROJECT_ROOT / "data"
DATA_DIR.mkdir(exist_ok=True)                 # create once
HISTORY_FILE = DATA_DIR / "chat_history.json"

def load_history():
    try:
        if HISTORY_FILE.exists():
            content = HISTORY_FILE.read_text(encoding="utf-8")
            if content.strip():
                return json.loads(content)
    except (json.JSONDecodeError, Exception) as e:
        print(f"Error loading history: {e}")
    return []

def clear_history():
    try:
        HISTORY_FILE.unlink(missing_ok=True)
    except Exception as e:
        print(f"Error clearing history: {e}")
    return []

def save_history(history):
    try:
        # Filter out empty messages before saving
        filtered_history = []
        for msg in history:
            if isinstance(msg, dict) and msg.get("content", "").strip():
                filtered_history.append(msg)
        
        print(f"Saving {len(filtered_history)} messages to {HISTORY_FILE}")  # Debug
        HISTORY_FILE.write_text(
            json.dumps(filtered_history, indent=2, ensure_ascii=False),
            encoding="utf-8",
        )
        print(f"Successfully saved history file")  # Debug
    except Exception as e:
        print(f"Error saving history: {e}")
        import traceback
        traceback.print_exc()

# ─────────────────────────────────────────────
# streaming chat wrapper
# ─────────────────────────────────────────────
def chat_wrapper(message, history):
    if not message or not message.strip():
        return "", history or []
    
    history = history or []
    print(f"Starting chat_wrapper with history length: {len(history)}")  # Debug
    
    # Add user message
    history.append({"role": "user", "content": message.strip()})
    
    # Initialize assistant message
    history.append({"role": "assistant", "content": ""})
    
    # Clear the input field and show user message immediately
    yield "", history
    
    # Generate response
    response_generated = False
    full_response = ""
    
    try:
        print(f"Generating response for: {message.strip()}")  # Debug
        for token in generate_response(message.strip(), history[:-1]):  # Don't include the empty assistant message
            if token:  # Process all tokens, including spaces
                full_response += token
                history[-1]["content"] = full_response
                response_generated = True
                yield "", history
    except Exception as e:
        print(f"Error in chat_wrapper: {e}")
        import traceback
        traceback.print_exc()
        history[-1]["content"] = "I encountered an error while processing your request. Please try again."
        response_generated = True
        yield "", history
    
    # If no response was generated, provide a fallback
    if not response_generated or not history[-1]["content"].strip():
        print("No response generated, using fallback")  # Debug
        history[-1]["content"] = ("I'm having trouble generating a response. "
                                 "Please visit https://www.nileedgeinnovations.org "
                                 "or contact us for assistance.")
        yield "", history
    
    print(f"Final response length: {len(history[-1]['content'])}")  # Debug
    print(f"Final history length: {len(history)}")  # Debug
    
    # Save the updated history - CRITICAL: This was missing proper execution
    try:
        save_history(history)
        print("History saved successfully")  # Debug
    except Exception as e:
        print(f"Failed to save history: {e}")
        import traceback
        traceback.print_exc()

# ─────────────────────────────────────────────
# build UI
# ─────────────────────────────────────────────
def build_interface():
    with gr.Blocks(title="Ask NileEdge AI", theme=gr.themes.Soft()) as demo:
        gr.Markdown("## Ask NileEdge AI")
        gr.Markdown("*Your intelligent assistant for AI solutions, data science, and digital transformation.*")

        chatbot = gr.Chatbot(
            value=load_history(),
            height=500,
            type="messages",
            show_copy_button=True,
            bubble_full_width=False,
        )
        
        with gr.Row():
            msg = gr.Textbox(
                placeholder="Type your question here...",
                container=False,
                scale=7,
                min_width=0,
            )
            send_btn = gr.Button("Send", variant="primary", scale=1, min_width=0)
        
        with gr.Row():
            clear_btn = gr.Button("Clear Chat", variant="secondary")
            save_btn = gr.Button("Save Chat", variant="secondary")

        # Event handlers
        send_event = send_btn.click(
            chat_wrapper, 
            inputs=[msg, chatbot], 
            outputs=[msg, chatbot],
            show_progress=True,
        )
        
        submit_event = msg.submit(
            chat_wrapper, 
            inputs=[msg, chatbot], 
            outputs=[msg, chatbot],
            show_progress=True,
        )

        def clear_and_save():
            """Clear chat and save empty history"""
            save_history([])
            return "", []

        clear_btn.click(
            clear_and_save,
            outputs=[msg, chatbot], 
            queue=False,
        )
        
        def manual_save(history):
            save_history(history)
            return history
        
        save_btn.click(
            manual_save,
            inputs=[chatbot],
            outputs=[chatbot],
            queue=False,
        )

        # Add some styling
        demo.css = """
        .gradio-container {
            max-width: 1000px !important;
        }
        """

    return demo

# ─────────────────────────────────────────────
if __name__ == "__main__":
    import atexit
    
    # Register cleanup functions
    atexit.register(save_data)       # persist FAQ cache & chat log
    
    # Ensure data directory exists
    DATA_DIR.mkdir(exist_ok=True)
    
    # Load initial history to verify it works
    initial_history = load_history()
    print(f"Loaded {len(initial_history)} messages from history")
    print(f"History file path: {HISTORY_FILE.absolute()}")
    print(f"History file exists: {HISTORY_FILE.exists()}")
    
    # Test save functionality
    test_history = [{"role": "user", "content": "test"}, {"role": "assistant", "content": "test response"}]
    save_history(test_history)
    
    # Launch the interface
    demo = build_interface()
    demo.launch(
        share=True,
        server_name="0.0.0.0",
        server_port=7860,
        show_error=True,
    )