# NileEdge AI Assistant

The **NileEdge AI Assistant** is a locally hosted system that combines:

- A chatbot that answers questions using context-aware reasoning
- An email agent that automatically replies to customer messages

It provides accurate responses using:

* Semantic FAQ matching
* Vector-based document retrieval
* Local LLM inference (e.g., Mistral)
* Audio transcription using Whisper
* A custom web interface (HTML/CSS/JS)

This assistant is private, extendable, and runs entirely on your machine.

---

## Project Goals

* Provide meaningful answers about NileEdge Innovations
* Minimize LLM usage through semantic caching
* Use local models and embeddings to preserve privacy
* Enable audio-based queries
* Automate professional email responses
* Log all queries and interactions for improvement

---

## File Structure

```
response_aigent/
├── .gradio/                      # Optional Gradio session files
├── app/                          # Core logic
│   ├── __init__.py
│   ├── chatbot.py                # Chatbot pipeline
│   ├── config.py                 # Configuration (API keys, paths)
│   ├── email_agent.py            # Email responder logic
│   ├── retrieval.py              # Vector similarity logic
│   ├── scraper.py                # Scraping for vector DB
│   └── llm/                      # LLM backend wrapper
│
├── assets/                       # (If used for icons/images)
├── data/                         # Chat and knowledge data
│   ├── chat_history.json
│   ├── faq_cache.json
│   ├── questions_log.json
│   ├── scraped_pages.json
│   └── website_data.json
│
├── logs/                         # Email/server logs
├── models/                       # Local LLM models (.gguf)
├── nileedge_venv/                # Python virtual environment
├── scripts/
│   └── refresh_kb.py             # Rebuild vector database
│
├── static/                       # Frontend styles/images
├── templates/
│   └── chat.html                 # Web chat interface
│
├── .env                          # Email and model env variables
├── .gitignore
├── launch.sh                     # Bash launcher for server + agent
├── launch.bat                    # Windows launcher (optional)
├── README.md
├── requirements.txt              # Python dependencies
├── run_chatbot.py                # (Optional legacy Gradio UI)
├── server.py                     # Flask app for chat
├── steps.md                      # Setup guide (if used)
└── supervisord.conf              # Persistent daemon runner config
```

---

## Setup Instructions

### 1. Clone the Repository

```bash
git clone https://github.com/your-username/response_aigent.git
cd response_aigent
```

### 2. Set Up Python 3.11 Environment

```bash
python -m venv nileedge_venv
nileedge_venv\Scripts\activate       # On Windows
# OR
source nileedge_venv/bin/activate    # On macOS/Linux
```

### 3. Install Required Packages

```bash
pip install -r requirements.txt
```

Also ensure `ffmpeg` is installed for Whisper:

- Windows: [Download FFmpeg](https://ffmpeg.org/download.html) and add to PATH
- Linux: `sudo apt install ffmpeg`

---

### 4. Prepare the Model

Download a `.gguf` quantized LLM (e.g. Mistral) and place it in `models/`.
Ensure `config.py` points to the correct file.

---

### 5. Build the Vector Knowledge Base

```bash
python scripts/refresh_kb.py
```

This scrapes + embeds the knowledge base for the assistant.

---

### 6. Run Both Chatbot and Email Agent

#### Option A: Bash (Linux/macOS)
```bash
bash launch.sh
```

#### Option B: Windows
```bat
launch.bat
```

#### Option C: Supervisor (Cross-platform, daemon mode)
```bash
supervisord -c supervisord.conf
```

Both services will run persistently, restart if they fail, and log output to the `logs/` directory.

---

## Features

* Natural chat interface with voice and text
* Handles both typed and spoken questions
* Automatically replies to incoming emails
* Uses FAQ, embeddings, and LLM to answer questions
* Clean, branded frontend UI
* Works entirely offline after setup

---

## Logging

* `data/chat_history.json` – Chat logs
* `data/questions_log.json` – New questions to improve
* `data/faq_cache.json` – Cached FAQs
* `sent_log.txt` – Email reply history with status
* `logs/*.log` – Live server/email logs

---

## Customization

* Change website sources in `refresh_kb.py`
* Replace UI in `templates/chat.html` and `static/style.css`
* Add new fallback rules or auto-reply tone in `email_agent.py`
* Swap in your preferred `.gguf` LLM model

---

## License

This project is licensed under the MIT License.
