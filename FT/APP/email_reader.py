import imaplib
import email
from email.header import decode_header
import getpass
import codecs

IMAP_SERVER = "imap.gmail.com"
EMAIL_ACCOUNT = "hackatonaccenture2025@gmail.com"
EMAIL_PASSWORD = "yzzz laul yxnc qzuy"

def clean_text(text):
    """Remove newlines and excessive whitespace."""
    return " ".join(text.split())

def fetch_emails(date_from, date_to, output_file=None):
    mail = imaplib.IMAP4_SSL(IMAP_SERVER)
    mail.login(EMAIL_ACCOUNT, EMAIL_PASSWORD)
    mail.select("inbox")

    status, data = mail.search(None, f'(SINCE "{date_from}" BEFORE "{date_to}")')
    email_ids = data[0].split()
    emails = []

    for e_id in email_ids:
        status, msg_data = mail.fetch(e_id, "(RFC822)")
        raw_email = msg_data[0][1]
        msg = email.message_from_bytes(raw_email)

        # Decode email subject
        subject, encoding = decode_header(msg["Subject"])[0]
        if isinstance(subject, bytes):
            try:
                if encoding and encoding.lower() in codecs.encodings_aliases:
                    subject = subject.decode(encoding, errors="ignore")
                else:
                    subject = subject.decode("utf-8", errors="ignore")
            except Exception:
                subject = subject.decode("utf-8", errors="ignore")

        # Get email body
        body = ""
        if msg.is_multipart():
            for part in msg.walk():
                if part.get_content_type() == "text/plain" and not part.get("Content-Disposition"):
                    try:
                        body = part.get_payload(decode=True).decode(part.get_content_charset() or "utf-8")
                        break
                    except:
                        body = ""
        else:
            try:
                body = msg.get_payload(decode=True).decode(msg.get_content_charset() or "utf-8")
            except:
                body = ""

        cleaned_body = clean_text(body)
        emails.append({"subject": subject, "body": cleaned_body})

    if output_file:
        with open(output_file, "w", encoding="utf-8") as f:
            for item in emails:
                f.write(f"Subject: {item['subject']}\nBody: {email['body']}\n{'-'*40}\n")

    return emails

if __name__ == "__main__":
    date_from = "14-May-2025"
    date_to = "17-May-2025"
    fetch_emails(date_from, date_to, "emails_14_15_maio.txt")
