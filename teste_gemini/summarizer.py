import os
import google.generativeai as genai
from dotenv import load_dotenv

load_dotenv()
api_key = os.getenv("GEMINI_API_KEY")
genai.configure(api_key=api_key)

def summarize_emails(
    emails,
    prioritize_keywords=None,
    deprioritize_keywords=None,
    more_relevant_conversations=None,
    less_relevant_conversations=None
):
    """
    emails: lista de strings (e-mails)
    prioritize_keywords: lista de palavras-chave a priorizar
    deprioritize_keywords: lista de palavras-chave a despriorizar
    more_relevant_conversations: lista de tópicos/conversas mais relevantes
    less_relevant_conversations: lista de tópicos/conversas menos relevantes
    """
    prompt = "Resuma os seguintes e-mails em formato digerível, em 2-3 frases por e-mail."
    if prioritize_keywords:
        prompt += f"\nPriorize os seguintes tópicos/palavras: {', '.join(prioritize_keywords)}."
    if deprioritize_keywords:
        prompt += f"\nDespriorize os seguintes tópicos/palavras: {', '.join(deprioritize_keywords)}."
    if more_relevant_conversations:
        prompt += f"\nConsidere estas conversas como mais relevantes: {', '.join(more_relevant_conversations)}."
    if less_relevant_conversations:
        prompt += f"\nConsidere estas conversas como menos relevantes: {', '.join(less_relevant_conversations)}."
    prompt += "\n\nE-mails:\n"
    for idx, email in enumerate(emails, 1):
        prompt += f"{idx}. {email}\n"

    try:
        model = genai.GenerativeModel('gemini-pro')
        response = model.generate_content(prompt)
        return response.text.strip()
    except Exception as e:
        print(f"Erro ao resumir: {e}")
        return None