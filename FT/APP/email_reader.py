# email_reader.py

import imaplib
import email
from email.header import decode_header

IMAP_SERVER = "imap.gmail.com"
EMAIL_ACCOUNT = "hackatonaccenture2025@gmail.com"
EMAIL_PASSWORD = "yzzz laul yxnc qzuy"

def clean_text(text):
    return " ".join(text.split())

def fetch_emails(date_from, date_to, max_emails=20):
    mail = imaplib.IMAP4_SSL(IMAP_SERVER)
    mail.login(EMAIL_ACCOUNT, EMAIL_PASSWORD)
    mail.select("inbox")

    status, data = mail.search(None,
                               f'(SINCE "{date_from}" BEFORE "{date_to}")')

    email_ids = data[0].split()[-max_emails:]  # últimos X emails
    emails = []

    for e_id in email_ids:
        status, msg_data = mail.fetch(e_id, "(RFC822)")
        raw_email = msg_data[0][1]
        msg = email.message_from_bytes(raw_email)

        subject, encoding = decode_header(msg["Subject"])[0]
        if isinstance(subject, bytes):
            subject = subject.decode(encoding or "utf-8", errors="ignore")

        body = ""
        if msg.is_multipart():
            for part in msg.walk():
                if part.get_content_type() == "text/plain" and not part.get("Content-Disposition"):
                    body = part.get_payload(decode=True).decode(part.get_content_charset() or "utf-8", errors="ignore")
                    break
        else:
            body = msg.get_payload(decode=True).decode(msg.get_content_charset() or "utf-8", errors="ignore")

        emails.append({
            "subject": subject.strip(),
            "body": clean_text(body)
        })

    mail.logout()
    return emails
