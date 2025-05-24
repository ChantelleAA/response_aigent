import sys
import os
import json
import time
from collections import OrderedDict
from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from app.retrieval import query_vector_store
from app.config import VECTOR_COLLECTION, MODEL_PATH
from llama_cpp import Llama

os.environ['TF_ENABLE_ONEDNN_OPTS'] = '0'
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '2'

llm = Llama(model_path=MODEL_PATH, n_ctx=2048, n_threads=4)
embedder = SentenceTransformer("all-MiniLM-L6-v2")

# Load or initialize cache
CACHE_FILE = "data/faq_cache.json"
QUESTION_LOG_FILE = "data/questions_log.json"
CACHE_LIMIT = 1000

# Load cache
try:
    with open(CACHE_FILE, "r", encoding="utf-8") as f:
        content = f.read().strip()
        response_cache = json.loads(content) if content else {}
except (FileNotFoundError, json.JSONDecodeError):
    response_cache = {}

# Keep cache ordered
response_cache = OrderedDict(response_cache)

# Load question log
try:
    with open(QUESTION_LOG_FILE, "r", encoding="utf-8") as f:
        content = f.read().strip()
        question_log = json.loads(content) if content else []
except (FileNotFoundError, json.JSONDecodeError):
    question_log = []


def semantic_faq_match(user_input):
    if not response_cache:
        return None

    user_embedding = embedder.encode([user_input])[0]
    questions = list(response_cache.keys())
    question_embeddings = embedder.encode(questions)

    similarities = cosine_similarity([user_embedding], question_embeddings)[0]
    best_idx = similarities.argmax()
    if similarities[best_idx] >= 0.85:
        matched_question = questions[best_idx]
        print(f"[FAQ MATCH] Matched: {matched_question}")
        return response_cache[matched_question]["answer"]

    return None

# Generate response
def generate_response(user_input, history=None):

    if not user_input.strip():
        return "Please enter a valid question so I can assist you."

    key = user_input.strip().lower()

    faq_answer = semantic_faq_match(user_input)

    if faq_answer:
        return faq_answer

    question_log.append({
        "question": key,
        "timestamp": time.strftime("%Y-%m-%d %H:%M:%S")
    })

    if key in response_cache:
        print(f"[CACHE HIT] \"{user_input}: {key}\"")
        response_cache.move_to_end(key)
        return response_cache[key]["answer"]

    context_list = query_vector_store(user_input, VECTOR_COLLECTION)
    context = "\n".join(context_list)

    memory = ""
    if history:
        for q, a in history[-5:]:
            memory += f"User: {q}\nAssistant: {a}\n"

    prompt = f"""
    You are a friendly, professional assistant for NileEdge Innovations, a company offering AI solutions, data science, automation, and digital transformation.

    Be polite, helpful, and clear in your responses. If the question is not fully answerable with the information provided, kindly suggest visiting https://www.nileedgeinnovations.org or contacting the support team. Always maintain a respectful tone.

    Only use the information provided in the "Context" section to answer. Avoid guessing or making up information.

    Context:
    {context}

    {memory}User: {user_input}
    Assistant:"""

    response = llm(prompt=prompt, max_tokens=512, stop=["User:", "Assistant:"])
    answer = response["choices"][0]["text"].strip()
    if not answer or len(answer.split()) < 5:
        return "I'm not entirely sure how to answer that. You can visit our website at https://www.nileedgeinnovations.org or contact us for assistance. We're happy to help!"

    response_cache[key] = {
        "answer": answer,
        "timestamp": time.strftime("%Y-%m-%d %H:%M:%S")
    }

    if len(response_cache) > CACHE_LIMIT:
        del response_cache[next(iter(response_cache))]

    return answer

# Save data
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
