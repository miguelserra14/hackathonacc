import google.generativeai as genai
import os
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
    emails: lista de strings (e-mails simples) ou lista de dicionários (e-mails avançados)
    Cada dicionário pode ter campos como: assunto, remetente, data, corpo, etc.
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

    irrelevantes = []

    for idx, email in enumerate(emails, 1):
        motivo = None
        email_str = ""
        if isinstance(email, dict):
            if 'assunto' in email:
                email_str += f"Assunto: {email['assunto']}\n"
                if "newsletter" in email['assunto'].lower():
                    motivo = "contém uma newsletter e é irrelevante para o resumo"
            if 'remetente' in email:
                email_str += f"Remetente: {email['remetente']}\n"
            if 'data' in email:
                email_str += f"Data: {email['data']}\n"
            if 'corpo' in email:
                corpo = email['corpo']
                if "newsletter" in corpo.lower():
                    idx_news = corpo.lower().find("newsletter")
                    parte_relevante = corpo[:idx_news].strip()
                    if parte_relevante:
                        email_str += f"Corpo: {parte_relevante}\n"
                        # Não marca como irrelevante, pois há parte relevante
                    else:
                        motivo = "contém uma newsletter e é irrelevante para o resumo"
                else:
                    email_str += f"Corpo: {corpo}\n"
            # Só adiciona ao prompt se houver parte relevante (Corpo: presente e não vazio)
            if 'Corpo:' in email_str and email_str.strip().split('Corpo:')[1].strip():
                prompt += f"{idx}.\n{email_str}\n"
            elif motivo:
                irrelevantes.append((idx, motivo))
        else:
            # Assume string simples
            if "newsletter" in email.lower():
                idx_news = email.lower().find("newsletter")
                parte_relevante = email[:idx_news].strip()
                if parte_relevante:
                    prompt += f"{idx}. {parte_relevante}\n"
                    # Não marca como irrelevante, pois há parte relevante
                else:
                    motivo = "contém uma newsletter e é irrelevante para o resumo"
                    irrelevantes.append((idx, motivo))
            else:
                prompt += f"{idx}. {email}\n"

    if irrelevantes:
        irrelevantes_str = "; ".join([f"E-mail {i} ({motivo})" for i, motivo in irrelevantes])
        prompt += f"\nOs seguintes e-mails foram considerados irrelevantes: {irrelevantes_str}.\n"

    try:
        model = genai.GenerativeModel('models/gemini-1.5-flash-latest')
        response = model.generate_content(prompt)
        return response.text.strip()
    except Exception as e:
        print(f"Erro ao resumir: {e}")
        return None