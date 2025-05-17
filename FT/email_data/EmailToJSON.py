import json
import re

input_file = "emails.txt"
output_file = "email_dataJSON.json"

def clean_links_and_brackets(text):
    # Remove tudo entre < >
    text = re.sub(r"<[^>]*>", "", text)
    # Remove links (http, https, www)
    text = re.sub(r"http[s]?://\S+", "", text)
    text = re.sub(r"www\.\S+", "", text)
    # Remove [image: ...]
    text = re.sub(r"\[image: [^\]]+\]", "", text)
    # Remove caracteres unicode invisíveis mais comuns
    text = re.sub(r'[\u200e\u200f\u202a-\u202e\u2066-\u2069]', '', text)
    # Remove todos os caracteres de controlo Unicode (exceto newlines e tab)
    text = re.sub(r'[\x00-\x08\x0B\x0C\x0E-\x1F\x7F-\x9F\uFEFF]', '', text)
    # Remove outros símbolos estranhos/caixa
    text = ''.join(c for c in text if c.isprintable() or c in '\n\r\t')
    return text.strip()

emails = []
with open(input_file, "r", encoding="utf-8") as f:
    content = f.read()

# Usa o novo separador pedido
email_blocks = content.split('-------------------------------------------------------\n')

for block in email_blocks:
    block = block.strip()
    if not block:
        continue
    email_obj = {}
    body_lines = []
    in_body = False
    lines = block.split('\n')
    for i, line in enumerate(lines):
        if line.startswith("Message-ID:"):
            email_obj["id"] = clean_links_and_brackets(line.split(":", 1)[1].strip())
        elif line.startswith("Date:"):
            email_obj["data"] = clean_links_and_brackets(line.split(":", 1)[1].strip())
        elif line.startswith("From:"):
            email_obj["remetente"] = clean_links_and_brackets(line.split(":", 1)[1].strip())
        elif line.startswith("To:"):
            email_obj["destinatario"] = clean_links_and_brackets(line.split(":", 1)[1].strip())
        elif line.startswith("Subject:"):
            email_obj["Subject"] = clean_links_and_brackets(line.split(":", 1)[1].strip())
        elif line.startswith("X-Priority:"):
            email_obj["prioridade"] = clean_links_and_brackets(line.split(":", 1)[1].strip())
        elif line.startswith("Body:"):
            body_text = line[5:].strip(" :")
            body_lines.append(clean_links_and_brackets(body_text))
            in_body = True
        elif in_body:
            body_lines.append(clean_links_and_brackets(line))
    # Junta todas as linhas do corpo num único campo Body (removendo espaços duplicados)
    corpo_txt = " ".join(l for l in body_lines if l.strip())
    corpo_txt = re.sub(r'\s+', ' ', corpo_txt).strip()
    email_obj["Body"] = corpo_txt

    if email_obj:
        emails.append(email_obj)

with open(output_file, "w", encoding="utf-8") as f:
    json.dump(emails, f, indent=2, ensure_ascii=False)

print(f"{len(emails)} e-mails guardados em {output_file}")
