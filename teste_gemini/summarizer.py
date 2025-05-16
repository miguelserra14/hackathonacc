import google.generativeai as genai
import os
from dotenv import load_dotenv
import re
from collections import Counter

load_dotenv()
api_key = os.getenv("GEMINI_API_KEY")
genai.configure(api_key=api_key)

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
        "Irrelevant emails (x,y,z,etc):** These emails were considered irrelevant because they were phishing messages (x,y,z), "
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

    irrelevantes = []
    for idx, email in enumerate(emails, 1):
        motivo = None
        email_str = ""
        texto_completo = ""
        if isinstance(email, dict):
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
            if 'Body:' in email_str and email_str.strip().split('Body:')[1].strip() and not motivo:
                prompt += f"{idx}.\n{email_str}\n"
            elif motivo:
                irrelevantes.append((idx, motivo))
        else:
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
                continue
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
    return prompt


def extract_email_numbers(section_title, summary):
    pattern = rf"\*\*{section_title}:\*\*\s*(.*?)\n\s*\*\*"
    match = re.search(pattern, summary, re.DOTALL | re.IGNORECASE)
    if not match:
        pattern = rf"\*\*{section_title}:\*\*\s*(.*)"
        match = re.search(pattern, summary, re.DOTALL | re.IGNORECASE)
    if not match:
        return []
    section_text = match.group(1)
    email_nums = re.findall(r"Email ([\d, &]+):", section_text)
    numbers = []
    for group in email_nums:
        for part in re.split(r"[,&]", group):
            num = part.strip()
            if num.isdigit():
                numbers.append(int(num))
    return numbers

def extract_summary_stats(summary, emails):
    total_emails = len(emails)
    high = len(extract_email_numbers("High Priority", summary))
    medium = len(extract_email_numbers("Medium Priority", summary))
    low = len(extract_email_numbers("Low Priority", summary))
    irrelevant_match = re.search(r"Irrelevant emails\s*\(([\d,\s]+)\)", summary, re.IGNORECASE)
    if irrelevant_match:
        irrelevant = len([n for n in re.split(r"[,\s]+", irrelevant_match.group(1)) if n.isdigit()])
    else:
        irrelevant = 0
    remetentes = []
    for email in emails:
        if isinstance(email, dict) and 'remetente' in email:
            remetentes.append(email['remetente'])
    most_common_sender = Counter(remetentes).most_common(1)
    most_common_sender = most_common_sender[0][0] if most_common_sender else "Unknown"
    return total_emails, high, medium, low, irrelevant, most_common_sender

def build_info_text(total_emails, high, medium, low, irrelevant, most_common_sender):
    return (
        f"Summary of received emails:\n"
        f"- Total emails: {total_emails}\n"
        f"- High priority: {high}\n"
        f"- Medium priority: {medium}\n"
        f"- Low priority: {low}\n"
        f"- Irrelevant: {irrelevant}\n"
        f"- Most frequent sender/conversation: {most_common_sender}\n\n"
    )

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
        total_emails, high, medium, low, irrelevant, most_common_sender = extract_summary_stats(summary, emails)
        info_text = build_info_text(total_emails, high, medium, low, irrelevant, most_common_sender)
        return info_text + summary
    except Exception as e:
        print(f"Error summarizing: {e}")
        return None




