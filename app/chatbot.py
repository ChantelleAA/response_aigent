import sys
import os
import json
import time
from collections import OrderedDict

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from app.retrieval import query_vector_store
from app.config import VECTOR_COLLECTION, MODEL_PATH
from llama_cpp import Llama

os.environ['TF_ENABLE_ONEDNN_OPTS'] = '0'
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '2'

llm = Llama(model_path=MODEL_PATH, n_ctx=2048, n_threads=4)

# Load or initialize cache
CACHE_FILE = "data/faq_cache.json"
QUESTION_LOG_FILE = "data/questions_log.json"
CACHE_LIMIT = 1000

try:
    with open(CACHE_FILE, "r", encoding="utf-8") as f:
        response_cache = json.load(f)
except FileNotFoundError:
    response_cache = {}

# Keep cache ordered by access time
response_cache = OrderedDict(response_cache)

# Load or init question log
try:
    with open(QUESTION_LOG_FILE, "r", encoding="utf-8") as f:
        question_log = json.load(f)
except FileNotFoundError:
    question_log = []

def generate_response(user_input, history=None):
    key = user_input.strip().lower()

    question_log.append({
        "question": user_input,
        "timestamp": time.strftime("%Y-%m-%d %H:%M:%S")
    })

    if key in response_cache:
        print(f"[CACHE HIT] \"{user_input}\"")
        response_cache.move_to_end(key)
        return response_cache[key]["answer"]

    context_list = query_vector_store(user_input, VECTOR_COLLECTION)
    context = "\n".join(context_list)

    # Memory: include previous turns
    memory = ""
    if history:
        for q, a in history[-5:]:  # last 5 turns
            memory += f"User: {q}\nAssistant: {a}\n"

    prompt = f"""
        You are a helpful assistant for NileEdge Innovations.
        Use the following website information to answer user questions.

        Context:
        {context}

        {memory}User: {user_input}
        Assistant:
        """

    response = llm(prompt=prompt, max_tokens=512, stop=["User:", "Assistant:"])
    answer = response["choices"][0]["text"].strip()

    response_cache[key] = {
        "answer": answer,
        "timestamp": time.strftime("%Y-%m-%d %H:%M:%S")
    }

    if len(response_cache) > CACHE_LIMIT:
        del response_cache[next(iter(response_cache))]

    return answer


def save_data():
    with open(CACHE_FILE, "w", encoding="utf-8") as f:
        json.dump(response_cache, f, indent=2, ensure_ascii=False)
    with open(QUESTION_LOG_FILE, "w", encoding="utf-8") as f:
        json.dump(question_log, f, indent=2, ensure_ascii=False)

# Launch Gradio
if __name__ == "__main__":
    import gradio as gr
    import atexit
    atexit.register(save_data)

    def chat(user_message, history):
        reply = generate_response(user_message, history)
        history.append((user_message, reply))
        return history, history

    gr.ChatInterface(fn=chat, chatbot=gr.Chatbot(), title="Ask NileEdge AI").launch(share=True)
