from summarizer import summarize_emails

def parse_emails_from_file(filepath):
    emails = []
    with open(filepath, encoding="utf-8") as f:
        content = f.read()
    raw_emails = content.split('--- EMAIL END ---')
    for raw in raw_emails:
        if not raw.strip():
            continue
        email = {}
        lines = raw.strip().splitlines()
        body_lines = []
        in_body = False
        for line in lines:
            if line.startswith("Message-ID:"):
                email["id"] = line.split(":", 1)[1].strip()
            elif line.startswith("Date:"):
                email["data"] = line.split(":", 1)[1].strip()
            elif line.startswith("From:"):
                email["remetente"] = line.split(":", 1)[1].strip()
            elif line.startswith("To:"):
                email["destinatario"] = line.split(":", 1)[1].strip()
            elif line.startswith("Subject:"):
                email["assunto"] = line.split(":", 1)[1].strip()
            elif line.startswith("X-Priority:"):
                email["prioridade"] = line.split(":", 1)[1].strip()
            elif line.strip() == "":
                in_body = True
            elif in_body:
                body_lines.append(line)
        email["corpo"] = "\n".join(body_lines).strip()
        emails.append(email)
    return emails

def parse_topics_from_file(filepath):
    topics = []
    with open(filepath, encoding="utf-8") as f:
        for line in f:
            if "|" in line and not line.startswith("| **") and not line.startswith("|--"):
                topic = line.split("|")[1].strip()
                if topic and not topic.isdigit():
                    topics.append(topic)
    return topics

if __name__ == "__main__":
    emails = parse_emails_from_file("email_dataset.txt")
    # Se quiser usar tópicos como prioridade:
    # prioritize = parse_topics_from_file("email_dataset_topics.txt")
    # deprioritize = ["newsletter", "spam", "phishing", "recruitment", "job opportunities", "external news", "lottery", "seo"]
    prioritize = ["project", "client", "meeting", "security", "locklinked", "cvgen", "phoenix", "chimera", "alpha", "beta"]
    deprioritize = ["newsletter", "spam", "phishing", "recruitment", "job opportunities", "external news", "lottery", "seo"]

    resumo = summarize_emails(
        emails,
        prioritize_keywords=prioritize,
        deprioritize_keywords=deprioritize
    )
    print(resumo)