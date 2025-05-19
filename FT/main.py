import json
from summarizer import summarize_emails



def load_emails_from_json(json_path):
    with open(json_path, "r", encoding="utf-8") as f:
        emails = json.load(f)
    return emails

if __name__ == "__main__":
    # Lê os e-mails já convertidos para JSON pelo EmailToJSON.py
    emails = load_emails_from_json("email_dataJSON.json")
    print(f"Total emails loaded: {len(emails)}")
    # Exemplo de uso com summarize_emails
    prioritize = ["CRITICO","project", "client", "meeting", "security", "locklinked", "cvgen", "phoenix", "chimera", "alpha", "beta", "test","suspeito"]
    deprioritize = ["newsletter", "spam", "phishing", "recruitment", "job opportunities", "external news", "lottery", "seo"]

    resumo = summarize_emails(
        emails,
        prioritize_keywords=prioritize,
        deprioritize_keywords=deprioritize
    )
    print(resumo)