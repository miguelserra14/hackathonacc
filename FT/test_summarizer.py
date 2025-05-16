from summarizer import summarize_emails

def test_summarize_email():
    texto = ["Este é um e-mail de teste para verificar o resumo automático. recursos . reunião "]
    resumo = summarize_emails(texto)
    if resumo is not None and len(resumo) > 0:
        print("✅ Teste passou! Resumo gerado com sucesso:")
        print(resumo)
    else:
        print("❌ Teste falhou! Nenhum resumo foi gerado.")
        if resumo is None:
            print("Motivo: Função retornou None.")
        elif len(resumo) == 0:
            print("Motivo: Resumo vazio.")

if __name__ == "__main__":
    test_summarize_email()