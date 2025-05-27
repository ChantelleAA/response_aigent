# NileEdge AI Assistant

The **NileEdge AI Assistant** is a locally hosted chatbot built for NileEdge Innovations. It provides accurate, context-aware answers using:

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
* Log user queries for future improvements

---

## File Structure

```
response_aigent/
├── app/                        # Core logic (chatbot, retrieval, config)
├── assets/                     # (If used elsewhere, optional)
├── data/                       # Vector data and logs
│   ├── chat_history.json
│   ├── faq_cache.json
│   ├── questions_log.json
│   ├── scraped_pages.json
│   └── website_data.json
│
├── models/                     # Local quantized LLM (.gguf)
│   └── mistral.gguf
│
├── scripts/
│   └── refresh_kb.py           # Scrape and embed site content
│
├── static/                     # Frontend resources
│   ├── favicon.ico
│   ├── logo.png
│   ├── logo-round.png
│   ├── nileedge_logo_round.png
│   └── style.css
│
├── templates/
│   └── chat.html               # Chat interface template
│
├── server.py                   # Flask app entry point
├── app/email_agent.py          # Background email response script
├── launch.bat / launch.sh      # Run both scripts persistently
├── requirements.txt
├── .env
└── README.md
```

---

## Setup Instructions

### 1. Clone the Repository

```bash
git clone https://github.com/your-username/response_aigent.git
cd response_aigent
```

### 2. Set Up Python 3.11 Environment

Ensure you have Python 3.11 installed. Then:

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

Make sure `ffmpeg` is installed for audio transcription:

* On Linux: `sudo apt install ffmpeg`
* On Windows: [Download FFmpeg](https://ffmpeg.org/download.html) and add it to PATH

---

### 4. Prepare the LLM Model

Download a quantized `.gguf` model (e.g., Mistral) and place it in the `models/` directory.

Set the correct path in `app/config.py`.

---

### 5. Scrape and Embed Website Content

```bash
python scripts/refresh_kb.py
```

This generates `website_data.json` and populates the vector store.

---

### 6. Run Both Services Persistently

#### Option A: Using Supervisor (Recommended for Production)

1. Install Supervisor:
   ```bash
   pip install supervisor
   ```
2. Use the provided `supervisord.conf`, update paths, and run:
   ```bash
   supervisord -c supervisord.conf
   ```

#### Option B: Using Bash Script (Linux/macOS)

```bash
bash launch.sh
```

#### Option C: Using Batch Script (Windows)

```bat
launch.bat
```

These scripts will:
- Start the Flask server
- Start the email agent in `--mode scheduled`
- Log all output to `logs/`

---

## Features

* Supports both text and voice input
* Transcribes audio to text using Whisper
* Checks for known FAQ matches before calling the LLM
* Uses vector search for context from website data
* Clean, modern UI styled for the NileEdge brand
* Email responder supports retry logic and scheduled polling

---

## Logging

* `data/chat_history.json` – Full chat transcripts
* `data/questions_log.json` – New questions not in cache
* `data/faq_cache.json` – Stored Q&A for instant lookup
* `sent_log.txt` – Email replies with success/failure status
* `logs/*.log` – Output/error logs for both Flask and email agent

---

## Customization

* Edit `templates/chat.html` and `static/style.css` to adjust UI
* Use your own `.gguf` models in `models/`
* Modify `scripts/refresh_kb.py` to target other URLs
* Tweak vector search logic in `app/retrieval.py`
* Update email signature, fallback messages, or interval timing in `app/email_agent.py`

---

## License

This project is licensed under the MIT License.
