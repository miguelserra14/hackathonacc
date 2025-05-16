from teste_gemini.summarizer import summarize_emails

emails = [
    "Olá, equipe! A reunião foi remarcada para sexta-feira às 10h.",
    "O projeto X está atrasado. Precisamos de mais recursos."
]
prioritize = ["reunião", "projeto X"]
deprioritize = ["recursos"]

resumo = summarize_emails(
    emails,
    prioritize_keywords=prioritize,
    deprioritize_keywords=deprioritize
)
print(resumo)