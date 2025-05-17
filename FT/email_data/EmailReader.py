import imaplib
import email
import re

IMAP_SERVER = "imap.gmail.com"
EMAIL_ACCOUNT = "hackatonaccenture2025@gmail.com"
EMAIL_PASSWORD = "yzzz laul yxnc qzuy"

def extract_email(address):
    # Garante que address é string
    address = str(address or "")
    match = re.search(r"<([^>]+)>", address)
    if match:
        return match.group(1).strip()
    return address.strip()


def fetch_emails_raw(date_from, date_to, output_file="no.txt"):
    # Conecta
    mail = imaplib.IMAP4_SSL(IMAP_SERVER)
    mail.login(EMAIL_ACCOUNT, EMAIL_PASSWORD)
    mail.select("inbox")

    # Busca os emails nesse intervalo
    status, data = mail.search(None,
                               f'(SINCE "{date_from}" BEFORE "{date_to}")')

    email_ids = data[0].split()
    emails = []

    for e_id in email_ids:
        status, msg_data = mail.fetch(e_id, "(RFC822)")
        raw_email = msg_data[0][1]
        msg = email.message_from_bytes(raw_email)

        # Pega os headers principais (ou None se não existirem)
        subject = msg["Subject"]
        from_ = extract_email(msg["From"])
        to_ = extract_email(msg["To"])
        date_ = msg["Date"]
        message_id = msg["Message-ID"]

        # Corpo raw (primeiro text/plain)
        body = None
        if msg.is_multipart():
            for part in msg.walk():
                if part.get_content_type() == "text/plain":
                    body = part.get_payload(decode=True)
                    break
            if body is None:
                body = b""
        else:
            body = msg.get_payload(decode=True)
        
        # Decodifica body se for bytes, senão transforma em string crua
        if body:
            try:
                body = body.decode(errors="replace")
            except:
                body = str(body)
        else:
            body = ""

        # Monta output raw, separando pelo delimitador pedido
        emails.append(
            f"Message-ID: {message_id}\n"
            f"Date: {date_}\n"
            f"From: {from_}\n"
            f"To: {to_}\n"
            f"Subject: {subject}\n"
            f"Body:\n{body}\n"
            "-------------------------------------------------------\n"
        )

    with open(output_file, "w", encoding="utf-8") as f:
        f.writelines(emails)

    print(f"E-mails salvos em {output_file}")

if __name__ == "__main__":
    date_from = "14-May-2025"
    date_to = "17-May-2025"
    fetch_emails_raw(date_from, date_to, "emails.txt")
