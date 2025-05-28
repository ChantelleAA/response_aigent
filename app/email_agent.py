import imaplib
import smtplib
import email
from email.mime.text import MIMEText
import argparse
import sys
import os
import time
from chatbot import semantic_faq_match

# Ensure imports work relative to project root
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.config import EMAIL_ADDRESS, EMAIL_PASSWORD, IMAP_SERVER, SMTP_SERVER, SMTP_PORT
from app.llm import get_engine

# Disable unnecessary TensorFlow logging
os.environ['TF_ENABLE_ONEDNN_OPTS'] = '0'
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '2'

engine = get_engine()

FAILED_EMAILS = []
MAX_RETRIES = 3
RETRY_DELAY = 60  # seconds

# -----------------------------------------------------------------
# 1.  generate_email_response (replace the entire old function)
# -----------------------------------------------------------------
def generate_email_response(user_input: str, history=None) -> str:
    """
    Build a full, formal reply.  We now:
      • keep a stronger prompt
      • require ≥60 words
      • only fall back if the model completely fails
    """
    from app.retrieval import query_vector_store
    from app.config import VECTOR_COLLECTION

    # ─────────────────────────────────────────────────────────────
    # 0. Empty input → quick polite prompt for detail
    # ─────────────────────────────────────────────────────────────
    if not user_input.strip():
        return format_email_reply(
            "We received your message, but it seems there wasn’t enough detail "
            "for us to provide a specific answer just yet. "
            "Please let us know a bit more and we’ll be happy to help."
        )

    # ─────────────────────────────────────────────────────────────
    # 1. FAQ       → instant answer
    # ─────────────────────────────────────────────────────────────
    faq_ans = semantic_faq_match(user_input)
    if faq_ans:
        return format_email_reply(faq_ans)

    # ─────────────────────────────────────────────────────────────
    # 2. Vector search context
    # ─────────────────────────────────────────────────────────────
    try:
        context_list = query_vector_store(user_input, VECTOR_COLLECTION)
        context = "\n".join(context_list) if context_list else ""
    except Exception as e:
        print(f"[WARN] vector search failed: {e}")
        context = ""

    # ─────────────────────────────────────────────────────────────
    # 3. Prompt the local LLM
    # ─────────────────────────────────────────────────────────────
    prompt = f"""
You are a professional email assistant for NileEdge Innovations (AI, Data-Science, Automation).

Write a **formal email** in at least **60 words**.  
Always:
• Thank the customer for contacting us.  
• Address their question using ONLY the context if possible.  
• If context is weak, still give a helpful, reasonable answer (do *not* say you are uncertain).  
• Close by inviting them to visit the website or call.

Context:
{context if context else '[no extra context]'}

Customer message:
{user_input}

Email reply:
"""
    try:
        tokens = []
        # only ONE stop string so output isn't truncated immediately
        for tok in engine.stream(
            prompt,
            max_tokens=512,
            stop=["Customer message:"],
            temperature=0.7,
            top_p=0.9,
        ):
            tokens.append(tok)
        raw_reply = "".join(tokens).strip()
        print(f"[DEBUG] LLM raw reply →\n{raw_reply}\n")
    except Exception as e:
        print(f"[ERR] LLM failure: {e}")
        raw_reply = ""

    # ─────────────────────────────────────────────────────────────
    # 4. Minimal fallback only if model fully empty
    # ─────────────────────────────────────────────────────────────
    if not raw_reply:
        raw_reply = (
            "Thank you for reaching out. We are reviewing your question and "
            "will respond with detailed information shortly. "
            "Meanwhile, feel free to call or visit the website below."
        )

    return format_email_reply(raw_reply)


# def generate_email_response(user_input: str, history=None) -> str:
#     from app.retrieval import query_vector_store
#     from app.config import VECTOR_COLLECTION

#     key = user_input.strip().lower()

#     if not user_input.strip():
#         fallback = (
#             "We received your message, but it seems there wasn’t enough detail for us to provide a specific answer. "
#             "However, we're always happy to assist further."
#         )
#         return format_email_reply(fallback)

#     faq_ans = semantic_faq_match(user_input)
#     if faq_ans:
#         return format_email_reply(faq_ans)

#     try:
#         context_list = query_vector_store(user_input, VECTOR_COLLECTION)
#         context = "\n".join(context_list) if context_list else ""
#     except Exception as e:
#         print(f"Error querying vector store: {e}")
#         context = ""

#     prompt = f"""
# You are a professional email assistant for NileEdge Innovations, a company offering AI, Data Science, and Automation services.

# Your task is to write a full, formal email reply to a customer inquiry. Be confident and informative using the context provided.

# Instructions:
# - Start by thanking the customer for their message
# - Use the provided context to respond specifically to their concern
# - If context is weak, still try your best to infer an answer
# - Finish with a professional closing, and suggest visiting the website or calling

# Context:
# {context}

# Customer's Message:
# {user_input}

# Email Response:
# """
#     try:
#         tokens = []
#         for tok in engine.stream(prompt, max_tokens=512, stop=["Customer's Message:", "Email Response:"], temperature=0.7, top_p=0.9):
#             tokens.append(tok)
#         raw_reply = "".join(tokens).strip()
#     except Exception as e:
#         print(f"Error generating email reply: {e}")
#         raw_reply = (
#             "We appreciate your message. While we may need more details to respond accurately, "
#             "we’re here to help and ready to discuss further."
#         )

#     if len(raw_reply.split()) < 15 or any(phrase in raw_reply.lower() for phrase in ["i'm not sure", "don't know", "cannot answer"]):
#         raw_reply = (
#             "Thank you for your message. We’re happy to support you, although we may need a bit more information "
#             "to provide a complete answer. Please feel free to get in touch directly using the contact options below."
#         )

#     return format_email_reply(raw_reply)

def format_email_reply(main_content: str) -> str:
    salutation = "Dear Valued Customer,\n\n"
    thank_you = "Thank you for contacting NileEdge Innovations.\n\n"

    contact_details = (
        "\n\nFor more information, you can:\n"
        "• Visit our website: https://www.nileedgeinnovations.org\n"
        "• Call us at: +234 90 69210 225\n"
        "• Visit our office at:\n"
        "  NileEdge Innovations\n"
        "  17 Fatai Oloko Crescent\n"
        "  Lagos, Nigeria\n"
        "• Email us at: info@nileedgeinnovations.org"
    )

    closing = "\n\nBest regards,\nNileEdge Innovations Support Team"

    return f"{salutation}{thank_you}{main_content.strip()}{contact_details}{closing}"

def check_unread_emails():
    imap = imaplib.IMAP4_SSL(IMAP_SERVER)
    imap.login(EMAIL_ADDRESS, EMAIL_PASSWORD)
    imap.select("inbox")

    status, messages = imap.search(None, 'UNSEEN')
    if status != "OK":
        return []

    mail_ids = messages[0].split()
    unread_emails = []
    for mail_id in mail_ids:
        status, data = imap.fetch(mail_id, '(RFC822)')
        msg = email.message_from_bytes(data[0][1])
        subject = msg["subject"] or "Your Inquiry"
        from_addr = email.utils.parseaddr(msg["from"])[1]
        payload = msg.get_payload(decode=True)
        body = payload.decode() if payload else ""
        unread_emails.append({"from": from_addr, "subject": subject, "body": body})

    imap.logout()
    return unread_emails

def send_email(to_addr, subject, body):
    if hasattr(body, '__iter__') and not isinstance(body, str):
        body = "".join(body)

    msg = MIMEText(body, "plain", "utf-8")
    msg["Subject"] = f"Re: {subject or 'Your Inquiry'}"
    msg["From"] = EMAIL_ADDRESS
    msg["To"] = to_addr

    for attempt in range(MAX_RETRIES):
        try:
            smtp = smtplib.SMTP_SSL(SMTP_SERVER, SMTP_PORT)
            smtp.login(EMAIL_ADDRESS, EMAIL_PASSWORD)
            smtp.send_message(msg)
            smtp.quit()
            return True
        except Exception as e:
            print(f"Failed to send email to {to_addr}: {e} (Attempt {attempt + 1})")
            time.sleep(RETRY_DELAY)

    FAILED_EMAILS.append((to_addr, subject, body))
    return False

def process_emails():
    emails = check_unread_emails()
    print(f"[{time.strftime('%Y-%m-%d %H:%M:%S')}] Found {len(emails)} unread emails.")
    for mail in emails:
        print(f"\n--- Processing ---\nFrom: {mail['from']}\nSubject: {mail['subject']}\nBody:\n{mail['body']}")
        reply = generate_email_response(mail["body"])
        print(f"\nReplying with:\n{reply}")
        success = send_email(mail["from"], mail["subject"], reply)

        with open("sent_log.txt", "a", encoding="utf-8") as f:
            f.write(f"\nTo: {mail['from']}\nSubject: {mail['subject']}\nReply:\n{reply}\nStatus: {'Sent' if success else 'Failed'}\n{'-'*60}\n")

        if success:
            print("Response sent.")
        else:
            print("Failed to send response after retries.")

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--mode", choices=["manual", "scheduled"], default="manual")
    parser.add_argument("--interval", type=int, default=300, help="Interval in seconds between email checks")
    args = parser.parse_args()

    print(f"Running email agent in {args.mode} mode...")

    if args.mode == "manual":
        process_emails()
    else:
        while True:
            process_emails()
            print(f"Sleeping for {args.interval} seconds...")
            time.sleep(args.interval)