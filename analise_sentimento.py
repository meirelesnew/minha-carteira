import yfinance as yf
import pandas as pd
from openai import OpenAI
import json
from datetime import datetime, timedelta

# Configuração da OpenAI (pré-configurada no ambiente Manus)
client = OpenAI()

def buscar_noticias(ticker):
    """Busca notícias recentes do ativo via yfinance."""
    print(f"   🔍 Buscando notícias para {ticker}...")
    try:
        asset = yf.Ticker(ticker)
        news = asset.news
        return news if news else []
    except Exception as e:
        print(f"   ⚠️ Erro ao buscar notícias para {ticker}: {e}")
        return []

def analisar_sentimento_llm(noticias):
    """Usa LLM para analisar o sentimento das notícias e retornar uma nota de -1 a 1."""
    if not noticias:
        return 0.0  # Neutro se não houver notícias

    # Preparar o texto das notícias para o prompt
    texto_noticias = ""
    for i, n in enumerate(noticias[:5]):  # Limitar às 5 mais recentes
        titulo = n.get('title', '')
        texto_noticias += f"{i+1}. {titulo}\n"

    prompt = f"""
    Analise o sentimento das seguintes notícias financeiras para um investidor.
    Retorne APENAS um número entre -1.0 (muito negativo/pessimista) e 1.0 (muito positivo/otimista).
    0.0 representa um sentimento neutro.

    Notícias:
    {texto_noticias}

    Sentimento (apenas o número):
    """

    try:
        response = client.chat.completions.create(
            model="gpt-4.1-mini",
            messages=[{"role": "user", "content": prompt}],
            temperature=0
        )
        sentimento = response.choices[0].message.content.strip()
        return float(sentimento)
    except Exception as e:
        print(f"   ⚠️ Erro na análise de sentimento via LLM: {e}")
        return 0.0

def obter_score_fundamentalista(ticker):
    """Fluxo completo: busca notícias e gera score de sentimento."""
    noticias = buscar_noticias(ticker)
    score = analisar_sentimento_llm(noticias)
    print(f"   📊 Score de sentimento para {ticker}: {score}")
    return score

if __name__ == "__main__":
    # Teste rápido
    test_ticker = "MXRF11.SA"
    score = obter_score_fundamentalista(test_ticker)
    print(f"Resultado teste {test_ticker}: {score}")
