import google.generativeai as genai
import os
from dotenv import load_dotenv
import re

load_dotenv()
api_key = os.getenv("GEMINI_API_KEY")
genai.configure(api_key=api_key)

def format_email_dict(email, prioritize_keywords):
    email_str = ""
    texto_completo = ""
    motivo = None
    if 'assunto' in email:
        email_str += f"Subject: {email['assunto']}\n"
        texto_completo += email['assunto'] + " "
    if 'remetente' in email:
        email_str += f"From: {email['remetente']}\n"
    if 'data' in email:
        email_str += f"Date: {email['data']}\n"
    if 'corpo' in email:
        corpo = email['corpo']
        texto_completo += corpo
        if "newsletter" in corpo.lower():
            idx_news = corpo.lower().find("newsletter")
            parte_relevante = corpo[:idx_news].strip()
            if parte_relevante:
                email_str += f"Body: {parte_relevante}\n"
            else:
                motivo = "contains a newsletter and is irrelevant for the summary"
        else:
            email_str += f"Body: {corpo}\n"
    palavras_relevantes = (prioritize_keywords or [])
    if palavras_relevantes and not any(p.lower() in texto_completo.lower() for p in palavras_relevantes):
        motivo = "does not contain relevant information about the priority topics"
    return email_str, motivo

def format_email_str(email, prioritize_keywords, deprioritize_keywords):
    texto_completo = email
    motivo = None
    parte_relevante = None
    palavra_despriorizada = None
    if deprioritize_keywords:
        for palavra in deprioritize_keywords:
            if palavra.lower() in email.lower():
                palavra_despriorizada = palavra
                break
    if palavra_despriorizada:
        idx_despriorizada = email.lower().find(palavra_despriorizada.lower())
        parte_relevante = email[:idx_despriorizada].strip()
        if not parte_relevante:
            motivo = f"contains '{palavra_despriorizada}' and is irrelevant for the summary"
    palavras_relevantes = (prioritize_keywords or [])
    if palavras_relevantes and not any(p.lower() in texto_completo.lower() for p in palavras_relevantes):
        motivo = "does not contain relevant information about the priority topics"
    return parte_relevante, motivo, palavra_despriorizada

def build_prompt(
    emails,
    prioritize_keywords=None,
    deprioritize_keywords=None,
    more_relevant_conversations=None,
    less_relevant_conversations=None
):
    prompt = (
        "Summarize the following emails in a digestible format, using 2-3 sentences per email. "
        "Based on the content, divide the relevant emails into high, medium, and low priority. "
        "At the end, add a sentence with the numbers and causes of irrelevant emails in the following format: "
        "Irrelevant emails (x,y,z,etc): These emails were considered irrelevant because they were phishing messages (x,y,z), "
        "external security updates or newsletters (a,b,b,c,d,e), job proposals (f,g), training reminders (60), or support ticket updates (76) that did not provide information about the projects."
    )
    if prioritize_keywords:
        prompt += f"\nPrioritize the following topics/keywords: {', '.join(prioritize_keywords)}."
    if deprioritize_keywords:
        prompt += f"\nDeprioritize the following topics/keywords: {', '.join(deprioritize_keywords)}."
    if more_relevant_conversations:
        prompt += f"\nConsider these conversations as more relevant: {', '.join(more_relevant_conversations)}."
    if less_relevant_conversations:
        prompt += f"\nConsider these conversations as less relevant: {', '.join(less_relevant_conversations)}."
    prompt += "\n\nEmails:\n"

    for idx, email in enumerate(emails, 1):
        if isinstance(email, dict):
            subject = email.get("subject", "No Subject")
            body = email.get("body", "No Body")
            prompt += f"{idx}. Subject: {subject}\nBody: {body}\n\n"

    prompt += (
        "\nAt the end, also provide a short statistical summary in this format:\n"
        "- Total emails: number of the last email\n"
        "- High priority: <number>\n"
        "- Medium priority: <number>\n"
        "- Low priority: <number>\n"
        "- Irrelevant: Total emails - (High Priority + Medium Priority + Low Priority)\n"
        "- Most frequent sender/conversation: <sender>\n"
    )
    return prompt

def remove_statistical_summary(text):
    return re.sub(r"\*\*Statistical Summary:\*\*.*", "", text, flags=re.DOTALL).strip()

def summarize_emails(
    emails,
    prioritize_keywords=None,
    deprioritize_keywords=None,
    more_relevant_conversations=None,
    less_relevant_conversations=None
):
    prompt = build_prompt(
        emails,
        prioritize_keywords,
        deprioritize_keywords,
        more_relevant_conversations,
        less_relevant_conversations
    )
    print("Generated Prompt:\n", prompt)  # Debug print

    try:
        model = genai.GenerativeModel('models/gemini-1.5-flash-latest')
        response = model.generate_content(prompt)
        print("AI Response:\n", response.text)  # Debug print
        summary = response.text.strip()

        # Extract statistical summary from the response
        stats = {
            "total_emails": len(emails),
            "high_priority": summary.count("High Priority:"),
            "medium_priority": summary.count("Medium Priority:"),
            "low_priority": summary.count("Low Priority:"),
            "irrelevant": summary.count("Irrelevant emails:")
        }

        return {
            "summary_text": summary,
            "stats": stats
        }
    except Exception as e:
        print(f"Error summarizing: {e}")
        return None




