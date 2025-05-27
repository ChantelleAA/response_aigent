# NileEdge AI Assistant
<img width="80%" align="center" alt="NileEdge AI Chatbot demo"
src="https://github.com/ChantelleAA/response_aigent/blob/main/nileedgechatbot.gif" />

The NileEdge AI Assistant is a context-aware chatbot that answers queries about NileEdge Innovations using a combination of:

* Semantic FAQ matching
* Vector-based document retrieval
* Local language model (LLM) inference
* A simple Gradio interface

It is designed for efficient customer interaction and scalable knowledge support.


## Project Objectives

* Provide accurate, contextually relevant answers from company knowledge.
* Reduce LLM usage by using a semantic cache for known questions.
* Retrieve up-to-date context from scraped data using vector search.
* Log user queries for analysis and FAQ enrichment.
* Offer a locally hosted chatbot interface for privacy and flexibility.


## File Structure

```
response_aigent/
├── .gradio/                    # Gradio session files (if any)
├── app/
│   ├── __init__.py             # Marks 'app' as a Python package
│   ├── chatbot.py              # Core logic to handle chatbot flow
│   ├── config.py               # Configuration (paths, constants)
│   ├── email_agent.py          # Email handling (if enabled)
│   ├── retrieval.py            # Vector search and context fetching
│   ├── scraper.py              # Website scraping utilities
│   └── assets/                 # Static files (images/icons)
│       ├── bot_avatar.png
│       ├── favicon.ico
│       ├── logo.png
│       └── logo_small.png
│
├── data/                       # Cached and processed knowledge
│   ├── chat_history.json       # Stores complete chat sessions
│   ├── faq_cache.json          # Static cache for known FAQ matches
│   ├── questions_log.json      # Logs new questions
│   ├── scraped_pages.json      # Raw scraped text from the website
│   └── website_data.json       # Cleaned and preprocessed documents
│
├── models/
│   └── mistral.gguf            # Local quantized LLM model
│
├── scripts/
│   └── refresh_kb.py           # Script to scrape, clean, and embed data
│
├── .env                        # Environment variables (e.g., ports, keys)
├── .gitignore                  # Ignore Python cache, env, and logs
├── run_chatbot.py              # Entry-point script to launch the bot
├── requirements.txt            # Python dependencies
└── README.md                   # Project documentation
```


## Setup Instructions

### 1. Clone the Repository

```bash
git clone https://github.com/your-username/response_aigent.git
cd response_aigent
```

### 2. Set Up Your Environment

Create a virtual environment and activate it:

```bash
python3 -m venv venv
source venv/bin/activate     # macOS/Linux
venv\Scripts\activate        # Windows
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

### 4. Prepare the Model

Download and place your quantized model (e.g., Mistral) in the models/ directory. Update app/config.py with the correct path.

### 5. Populate the Vector Database

Run the script to scrape and embed website data:

```bash
python scripts/refresh_kb.py
```

This will store vectorized documents in the configured Chroma vector store.

### 6. Run the Chatbot

```bash
python run_chatbot.py
```

A Gradio interface will launch in your browser.


## How It Works

1. A user submits a question.
2. The bot checks for a high-similarity match in the faq\_cache.json.
3. If none is found:

   * The question is logged.
   * Related context is fetched via vector search.
   * A prompt is created and sent to the local LLM.
4. The answer is returned, logged, and optionally cached for future use.


## Logging and QA Improvement

* data/questions\_log.json logs new questions for future analysis.
* data/chat\_history.json stores full chat transcripts.
* To improve the assistant, periodically review the logs and update faq\_cache.json or source data.


## Customization Tips

* Modify app/scraper.py to target new URLs.
* Update app/config.py to change thresholds and settings.
* Replace the model in models/ if you prefer a different quantized LLM.


## License

This project is released under the MIT License.
