import imaplib
import smtplib
import email
from email.mime.text import MIMEText
import argparse
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from app.chatbot import generate_response
from app.config import EMAIL_ADDRESS, EMAIL_PASSWORD, IMAP_SERVER, SMTP_SERVER, SMTP_PORT
os.environ['TF_ENABLE_ONEDNN_OPTS'] = '0'
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '2'



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
    for mail in emails:
        print(f"Responding to: {mail['from']}")
        reply = generate_response(mail["body"])
        send_email(mail["from"], mail["subject"], reply)
        print("Response sent.")

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--mode", choices=["manual", "scheduled"], default="manual")
    args = parser.parse_args()

    print(f"Running email agent in {args.mode} mode...")
    process_emails()
