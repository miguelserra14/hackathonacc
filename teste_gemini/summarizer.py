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
    prompt = "Resume os seguintes e-mails em formato digerível, em 2-3 frases por e-mail. Com base no conteúdo, divide os mails relevantes em prioridade alta, média e baixa. No final mete uma frase com os números e as causas dos e-mails irrelevantes no seguinte formato E-mails irrelevantes (x,y,z,etc):**  Esses e-mails foram considerados irrelevantes porque eram mensagens de phishing (x,y,z), atualizações de segurança externas ou newsletters (a,b,b,c,d,e), propostas de emprego (f,g), lembretes de treinos (60), ou atualizações de tickets de suporte (76) que não forneciam informações sobre os projetos."
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

    total_emails = len(emails)
    alta, media, baixa, irrelevantes_count = 0, 0, 0, 0

    for idx, email in enumerate(emails, 1):
        motivo = None
        email_str = ""
        texto_completo = ""
        if isinstance(email, dict):
            if 'assunto' in email:
                email_str += f"Assunto: {email['assunto']}\n"
                texto_completo += email['assunto'] + " "
            if 'remetente' in email:
                email_str += f"Remetente: {email['remetente']}\n"
            if 'data' in email:
                email_str += f"Data: {email['data']}\n"
            if 'corpo' in email:
                corpo = email['corpo']
                texto_completo += corpo
                if "newsletter" in corpo.lower():
                    idx_news = corpo.lower().find("newsletter")
                    parte_relevante = corpo[:idx_news].strip()
                    if parte_relevante:
                        email_str += f"Corpo: {parte_relevante}\n"
                    else:
                        motivo = "contém uma newsletter e é irrelevante para o resumo"
                else:
                    email_str += f"Corpo: {corpo}\n"
            # Novo critério: se não contém nenhuma palavra-chave relevante, marca como irrelevante
            palavras_relevantes = (prioritize_keywords or [])
            if palavras_relevantes and not any(p.lower() in texto_completo.lower() for p in palavras_relevantes):
                motivo = "não contém informações relevantes sobre os tópicos prioritários"
            if 'Corpo:' in email_str and email_str.strip().split('Corpo:')[1].strip() and not motivo:
                prompt += f"{idx}.\n{email_str}\n"
            elif motivo:
                irrelevantes.append((idx, motivo))
        else:
            # Assume string simples
            texto_completo = email
            motivo = None
            parte_relevante = None
            # Verifica se há alguma palavra despriorizada no texto
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
                    motivo = f"contém '{palavra_despriorizada}' e é irrelevante para o resumo"
            palavras_relevantes = (prioritize_keywords or [])
            if palavras_relevantes and not any(p.lower() in texto_completo.lower() for p in palavras_relevantes):
                motivo = "não contém informações relevantes sobre os tópicos prioritários"
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
            prompt += f"Os e-mails {', '.join(map(str, phishing))} foram omitidos pois eram tentativas de phishing.  "
        if outros:
            prompt += "Outros e-mails foram omitidos pois eram mensagens irrelevantes ou externos com pouca informação sobre os projetos.\n"

    
    try:
        model = genai.GenerativeModel('models/gemini-1.5-flash-latest')
        response = model.generate_content(prompt)

        return response.text.strip()
    except Exception as e:
        print(f"Erro ao resumir: {e}")
        return None