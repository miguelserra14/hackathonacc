from summarizer import summarize_emails

emails = [
    {
        "assunto": "Reunião de sexta",
        "remetente": "joao@email.com",
        "data": "2024-05-16",
        "corpo": "Olá, equipe! A reunião foi remarcada para sexta-feira às 10h."
    },
    {
        "assunto": "Status do Projeto X",
        "remetente": "ana@email.com",
        "data": "2024-05-15",
        "corpo": "O projeto X está atrasado. Precisamos de mais recursos. leiam a Newsletter"
    },
    {
        "assunto": "Newsletter semanal",
        "remetente": "ana@email.com",
        "data": "2024-05-15",
        "corpo": "blababalalab"
    }
]
prioritize = ["reunião", "projeto X"]
deprioritize = ["Newsletter", "recursos"]

resumo = summarize_emails(
    emails,
    prioritize_keywords=prioritize,
    deprioritize_keywords=deprioritize
)
print(resumo)