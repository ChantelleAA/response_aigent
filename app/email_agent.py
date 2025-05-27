import imaplib
import smtplib
import email
from email.mime.text import MIMEText
import argparse
import sys
import os
from chatbot import semantic_faq_match

# Ensure imports work relative to project root
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.config import EMAIL_ADDRESS, EMAIL_PASSWORD, IMAP_SERVER, SMTP_SERVER, SMTP_PORT
from app.llm import get_engine

# Disable unnecessary TensorFlow logging
os.environ['TF_ENABLE_ONEDNN_OPTS'] = '0'
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '2'

engine = get_engine()

def generate_email_response(user_input: str, history=None) -> str:
    """Generates a formal, complete email reply with fallback logic."""
    from app.retrieval import query_vector_store
    from app.config import VECTOR_COLLECTION
    import time

    key = user_input.strip().lower()

    # Fallback for empty input
    if not user_input.strip():
        fallback = (
            "We received your message, but it seems there wasn’t enough detail for us to provide a specific answer. "
            "However, we're always happy to assist further."
        )
        return format_email_reply(fallback)

    # 1) semantic FAQ match
    faq_ans = semantic_faq_match(user_input)
    if faq_ans:
        return format_email_reply(faq_ans)

    # 2) vector store context
    try:
        context_list = query_vector_store(user_input, VECTOR_COLLECTION)
        context = "\n".join(context_list) if context_list else ""
    except Exception as e:
        print(f"Error querying vector store: {e}")
        context = ""

    # 3) LLM prompt
    prompt = f"""
You are a professional email assistant for NileEdge Innovations, a company offering AI, Data Science, and Automation services.

Your reply should:
- Thank the customer for contacting us
- Politely respond using the given context
- Encourage the customer to visit the website, call, or come to our office
- End with a professional sign-off

Context:
{context}

Customer's Message:
{user_input}

Email Response:
"""
    try:
        tokens = []
        for tok in engine.stream(prompt, max_tokens=512, stop=["Customer's Message:", "Email Response:"], temperature=0.7, top_p=0.9):
            tokens.append(tok)
        raw_reply = "".join(tokens).strip()
    except Exception as e:
        print(f"Error generating email reply: {e}")
        raw_reply = (
            "We appreciate your message. While we may need more details to respond accurately, "
            "we’re here to help and ready to discuss further."
        )

    # Fallback for low-confidence replies
    if len(raw_reply.split()) < 15 or any(phrase in raw_reply.lower() for phrase in ["i'm not sure", "don't know", "cannot answer"]):
        raw_reply = (
            "Thank you for your message. We’re happy to support you, although we may need a bit more information "
            "to provide a complete answer. Please feel free to get in touch directly using the contact options below."
        )

    return format_email_reply(raw_reply)

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
        subject = msg["subject"]
        from_addr = email.utils.parseaddr(msg["from"])[1]
        payload = msg.get_payload(decode=True)
        body = payload.decode() if payload else ""
        unread_emails.append({"from": from_addr, "subject": subject, "body": body})

    imap.logout()
    return unread_emails


def send_email(to_addr, subject, body):
    if hasattr(body, '__iter__') and not isinstance(body, str):
        body = "".join(body)

    msg = MIMEText(body)
    msg["Subject"] = f"Re: {subject}"
    msg["From"] = EMAIL_ADDRESS
    msg["To"] = to_addr

    smtp = smtplib.SMTP_SSL(SMTP_SERVER, SMTP_PORT)
    smtp.login(EMAIL_ADDRESS, EMAIL_PASSWORD)
    smtp.send_message(msg)
    smtp.quit()


def process_emails():
    emails = check_unread_emails()
    print(f"Found {len(emails)} unread emails.")
    for mail in emails:
        print(f"\n--- Processing ---\nFrom: {mail['from']}\nSubject: {mail['subject']}\nBody:\n{mail['body']}")
        reply = generate_email_response(mail["body"])
        print(f"\nReplying with:\n{reply}")
        send_email(mail["from"], mail["subject"], reply)

        with open("sent_log.txt", "a", encoding="utf-8") as f:
            f.write(f"\nTo: {mail['from']}\nSubject: {mail['subject']}\nReply:\n{reply}\n{'-'*60}\n")

        print("Response sent.")


import time

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

