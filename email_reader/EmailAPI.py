import imaplib
import email
from email.header import decode_header
import getpass

IMAP_SERVER = "imap.gmail.com"
EMAIL_ACCOUNT = "hackatonaccenture2025@gmail.com"
EMAIL_PASSWORD = "yzzz laul yxnc qzuy"

def clean_text(text):
    """Remove newlines and excessive whitespace."""
    return " ".join(text.split())

def fetch_emails_plain(date_from, date_to, output_file="emails.txt"):
    # Connect to the server
    mail = imaplib.IMAP4_SSL(IMAP_SERVER)
    mail.login(EMAIL_ACCOUNT, EMAIL_PASSWORD)
    mail.select("inbox")

    # Search for emails in date range
    status, data = mail.search(None,
                               f'(SINCE "{date_from}" BEFORE "{date_to}")')

    email_ids = data[0].split()
    emails = []

    for e_id in email_ids:
        status, msg_data = mail.fetch(e_id, "(RFC822)")
        raw_email = msg_data[0][1]
        msg = email.message_from_bytes(raw_email)

        # Decode email subject
        subject, encoding = decode_header(msg["Subject"])[0]
        if isinstance(subject, bytes):
            subject = subject.decode(encoding or "utf-8")

        # Get email body
        body = ""
        if msg.is_multipart():
            for part in msg.walk():
                if part.get_content_type() == "text/plain" and not part.get("Content-Disposition"):
                    body = part.get_payload(decode=True).decode(part.get_content_charset() or "utf-8")
                    break
        else:
            body = msg.get_payload(decode=True).decode(msg.get_content_charset() or "utf-8")

        cleaned_body = clean_text(body)
        emails.append(f"Subject: {subject}\nBody: {cleaned_body}\n{'-'*40}\n")

    # Write emails to file
    with open(output_file, "w", encoding="utf-8") as f:
        f.writelines(emails)

    print(f"E-mails salvos em {output_file}")

if __name__ == "__main__":
    # 14-May-2025 até 15-May-2025 (BEFORE é exclusivo, então usar 16)
    date_from = "14-May-2025"
    date_to = "17-May-2025"
    fetch_emails_plain(date_from, date_to, "emails_14_15_maio.txt")
