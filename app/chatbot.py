import sys, os, json, time, pathlib
from collections import OrderedDict
from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from app.retrieval import query_vector_store
from app.config    import VECTOR_COLLECTION
from app.llm       import get_engine

os.environ["TF_ENABLE_ONEDNN_OPTS"] = "0"
os.environ["TF_CPP_MIN_LOG_LEVEL"]  = "2"

engine   = get_engine()                        # loads GGUF once
embedder = SentenceTransformer("all-MiniLM-L6-v2")

DATA_DIR           = pathlib.Path("data")
DATA_DIR.mkdir(exist_ok=True)

CACHE_FILE         = DATA_DIR / "faq_cache.json"
QUESTION_LOG_FILE  = DATA_DIR / "questions_log.json"
CACHE_LIMIT        = 1_000

def _load_json(path, default):
    try:
        txt = path.read_text(encoding="utf-8")
        return json.loads(txt) if txt.strip() else default
    except (FileNotFoundError, json.JSONDecodeError):
        return default

response_cache = OrderedDict(_load_json(CACHE_FILE, {}))
question_log   = _load_json(QUESTION_LOG_FILE, [])

def semantic_faq_match(user_input: str):
    if not response_cache:
        return None
    user_emb        = embedder.encode([user_input])[0]
    questions       = list(response_cache.keys())
    question_embeds = embedder.encode(questions)
    sims            = cosine_similarity([user_emb], question_embeds)[0]
    best_idx        = sims.argmax()
    if sims[best_idx] >= 0.85:
        return response_cache[questions[best_idx]]["answer"]
    return None

def generate_response(user_input: str, history=None):
    """Yields tokens so the UI can stream them."""
    if not user_input.strip():
        yield "Please enter a valid question so I can assist you."
        return

    key = user_input.strip().lower()

    # 1) semantic FAQ hit
    faq_ans = semantic_faq_match(user_input)
    if faq_ans:
        yield faq_ans
        return

    # 2) question log
    question_log.append({"question": key,
                         "timestamp": time.strftime("%Y-%m-%d %H:%M:%S")})

    # 3) literal cache hit
    if key in response_cache:
        response_cache.move_to_end(key)
        yield response_cache[key]["answer"]
        return

    # 4) RAG context + short memory
    try:
        context_list = query_vector_store(user_input, VECTOR_COLLECTION)
        context = "\n".join(context_list) if context_list else ""
    except Exception as e:
        print(f"Error querying vector store: {e}")
        context = ""

    memory = ""
    if history:
        # Convert Gradio message format to simple history
        valid_history = []
        if isinstance(history, list):
            for item in history[-10:]:  # Last 10 messages
                if isinstance(item, dict) and "role" in item and "content" in item:
                    if item["role"] == "user":
                        user_msg = item["content"]
                    elif item["role"] == "assistant" and item["content"].strip():
                        valid_history.append([user_msg, item["content"]])
                elif isinstance(item, (list, tuple)) and len(item) == 2:
                    valid_history.append(item)
        
        # Use last 5 exchanges for memory
        for q, a in valid_history[-5:]:
            if q and a:  # Ensure both are not empty
                memory += f"User: {q}\nAssistant: {a}\n"

    prompt = f"""
        You are a friendly, professional assistant for NileEdge Innovations, a company offering AI solutions, data science, automation, and digital transformation.

        Be polite, helpful, and clear in your responses. If the question is not fully answerable with the information provided, kindly suggest visiting https://www.nileedgeinnovations.org or contacting the support team.

        Only use the information provided in the "Context" section to answer. Avoid guessing.

        Context:
        {context}

        {memory}User: {user_input}
        Assistant:
        
        """

    answer_parts = []
    try:
        token_count = 0
        for tok in engine.stream(prompt,
                                 max_tokens=512,  # Increased from 256
                                 stop=["User:", "Assistant:"],
                                 temperature=0.7,
                                 top_p=0.9):
            if tok:  # Only yield non-empty tokens
                answer_parts.append(tok)
                yield tok
                token_count += 1
                
                # Safety check to prevent infinite loops
                if token_count > 1000:
                    break
    except Exception as e:
        print(f"Error generating response: {e}")
        fallback = ("I'm having trouble generating a response right now. "
                   "Please visit https://www.nileedgeinnovations.org "
                   "or contact us for assistance.")
        yield fallback
        return

    answer = "".join(answer_parts).strip()

    # Check if we got a meaningful response
    if not answer or len(answer.split()) < 3:
        fallback = ("I'm not entirely sure how to answer that. "
                    "Please visit https://www.nileedgeinnovations.org "
                    "or contact us for assistance.")
        yield fallback
        return

    # update cache (LRU)
    response_cache[key] = {
        "answer": answer,
        "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
    }
    if len(response_cache) > CACHE_LIMIT:
        del response_cache[next(iter(response_cache))]

    save_data()

def save_data():
    try:
        CACHE_FILE.write_text(json.dumps(response_cache,
                                         indent=2, ensure_ascii=False),
                              encoding="utf-8")
        QUESTION_LOG_FILE.write_text(json.dumps(question_log,
                                                indent=2, ensure_ascii=False),
                                     encoding="utf-8")
    except Exception as e:
        print(f"Error saving data: {e}")