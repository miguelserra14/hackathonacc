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

    # Usa 'Subject' e 'Body' se 'assunto' e 'corpo' não existirem
    assunto = email.get('assunto') or email.get('Subject', '')
    corpo = email.get('corpo') or email.get('Body', '')

    if assunto:
        email_str += f"Subject: {assunto}\n"
        texto_completo += assunto + " "
    if 'remetente' in email:
        email_str += f"From: {email['remetente']}\n"
    if 'data' in email:
        email_str += f"Date: {email['data']}\n"
    if corpo:
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
        "Irrelevant emails (examples:)** These emails were considered irrelevant because they were phishing messages, "
        "external security updates or newsletters, job proposals, training reminders, or support ticket updates that did not provide information about the projects."
    )
    if prioritize_keywords:
        prompt += f"\nPrioritize the following topics/keywords: {', '.join(prioritize_keywords)}, even if the body is brief or lacks detail. Prioritize subjects written in caps lock."
    if deprioritize_keywords:
        prompt += f"\nDeprioritize the following topics/keywords: {', '.join(deprioritize_keywords)}."
    if more_relevant_conversations:
        prompt += f"\nConsider these conversations as more relevant: {', '.join(more_relevant_conversations)}."
    if less_relevant_conversations:
        prompt += f"\nConsider these conversations as less relevant: {', '.join(less_relevant_conversations)}."
    prompt += "\n\nEmails:\n"

    irrelevantes = []
    for idx, email in enumerate(emails, 1):
        if isinstance(email, dict):
            email_str, motivo = format_email_dict(email, prioritize_keywords)
            if 'Body:' in email_str and email_str.strip().split('Body:')[1].strip() and not motivo:
                prompt += f"{idx}.\n{email_str}\n"
            elif motivo:
                irrelevantes.append((idx, motivo))
        else:
            parte_relevante, motivo, palavra_despriorizada = format_email_str(email, prioritize_keywords, deprioritize_keywords)
            if motivo:
                irrelevantes.append((idx, motivo))
            elif parte_relevante:
                prompt += f"{idx}. {parte_relevante}\n"
            elif not palavra_despriorizada:
                prompt += f"{idx}. {email}\n"
    phishing = [i for i, motivo in irrelevantes if "phishing" in motivo]
    outros = [i for i, motivo in irrelevantes if "phishing" not in motivo]
    if irrelevantes:
        prompt += "\n"
        if phishing:
            prompt += f"Emails {', '.join(map(str, phishing))} were omitted because they were phishing attempts.  "
        if outros:
            prompt += "Other emails were omitted because they were irrelevant messages or external with little project information.\n"

    prompt += (
        "\nAt the end, also provide a short statistical summary in this format:\n"
        f"- Total emails:{len(emails)} \n"
        "- High priority: <number>\n"
        "- Medium priority: <number>\n"
        "- Low priority: <number>\n"
        "- Irrelevant: Total emails - (High Priority + Medium Priority + Low Priority\n"
        "- Most frequent sender/conversation: <sender>\n"
    )
    return prompt


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
    try:
        model = genai.GenerativeModel('models/gemini-1.5-flash-latest')
        response = model.generate_content(prompt)
        summary = response.text.strip()
       
        return summary
    except Exception as e:
        print(f"Error summarizing: {e}")
        return None




