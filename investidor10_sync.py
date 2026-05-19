import os
import requests
from bs4 import BeautifulSoup
import json
import re

# IMPORTANTE: As credenciais devem ser configuradas no GitHub Secrets
# Não coloque seu login e senha aqui!
INVESTIDOR10_USER = os.environ.get('INVESTIDOR10_USER')
INVESTIDOR10_PASS = os.environ.get('INVESTIDOR10_PASS')

def login_investidor10():
    """Realiza o login no Investidor 10 e retorna a sessão."""
    if not INVESTIDOR10_USER or not INVESTIDOR10_PASS:
        print("❌ Erro: Credenciais não configuradas no ambiente (GitHub Secrets).")
        return None

    session = requests.Session()
    # User-agent para evitar bloqueios simples
    session.headers.update({
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
    })
    
    login_url = "https://investidor10.com.br/login/"
    
    try:
        # Primeiro acessa a página para pegar tokens se houver (CSRF)
        response = session.get(login_url)
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # O Investidor 10 usa um formulário simples, 
        # mas precisamos verificar se há campos ocultos de token
        payload = {
            'email': INVESTIDOR10_USER,
            'password': INVESTIDOR10_PASS,
            'redirect': ''
        }
        
        # Tenta realizar o login
        post_response = session.post(login_url, data=payload)
        
        # Verifica se o login foi bem sucedido (geralmente redireciona para a home logada)
        if post_response.status_code == 200 and ("Sair" in post_response.text or "minha-carteira" in post_response.url):
            print("✅ Login realizado com sucesso no Investidor 10!")
            return session
        else:
            print("⚠️ Falha no login. Verifique as credenciais nos GitHub Secrets.")
            return None
            
    except Exception as e:
        print(f"❌ Erro durante o login: {e}")
        return None

def extrair_ativos_carteira(session):
    """Extrai os ativos da carteira logada do Investidor 10."""
    if not session:
        return []
        
    carteira_url = "https://investidor10.com.br/minha-carteira/"
    try:
        response = session.get(carteira_url)
        soup = BeautifulSoup(response.text, 'html.parser')
        
        ativos = []
        # Lógica de extração baseada na estrutura da tabela de ativos do Investidor 10
        # O Investidor 10 costuma listar os ativos em tabelas ou cards
        # Esta é uma implementação baseada na estrutura comum de tabelas de ativos
        tabela = soup.find('table', {'id': 'table-wallet-stocks'}) # Exemplo de ID
        if not tabela:
            # Tenta encontrar por classes comuns se o ID não bater
            tabela = soup.find('table', class_=re.compile('table'))
            
        if tabela:
            rows = tabela.find_all('tr')[1:] # Pula o cabeçalho
            for row in rows:
                cols = row.find_all('td')
                if len(cols) >= 3:
                    ticker = cols[0].text.strip()
                    qtd = cols[1].text.strip()
                    preco_medio = cols[2].text.strip()
                    
                    # Limpeza de dados (remover R$, pontos, vírgulas)
                    try:
                        qtd = float(qtd.replace('.', '').replace(',', '.'))
                        preco_medio = float(preco_medio.replace('R$', '').replace('.', '').replace(',', '.').strip())
                        ativos.append({
                            "ticker": ticker,
                            "qtd": qtd,
                            "preco_medio": preco_medio
                        })
                    except:
                        continue
        
        print(f"📊 Encontrados {len(ativos)} ativos na carteira do Investidor 10.")
        return ativos
    except Exception as e:
        print(f"❌ Erro ao extrair dados da carteira: {e}")
        return []

def atualizar_dados_locais(novos_ativos):
    """Atualiza o arquivo dados.json com os ativos extraídos."""
    if not novos_ativos:
        return
        
    try:
        with open('dados.json', 'r', encoding='utf-8') as f:
            dados = json.load(f)
            
        # Atualiza carteira_acoes e carteira_fiis baseado no ticker
        # (Lógica simplificada para demonstração)
        for ativo in novos_ativos:
            ticker = ativo['ticker']
            # Verifica se é FII ou Ação (heurística simples: 11 no final = FII)
            is_fii = ticker.endswith('11')
            lista_alvo = 'carteira_fiis' if is_fii else 'carteira_acoes'
            
            encontrado = False
            for item in dados.get(lista_alvo, []):
                if item['ticker'] == ticker:
                    item['qtd'] = ativo['qtd']
                    item['preco_medio'] = ativo['preco_medio']
                    encontrado = True
                    break
            
            if not encontrado:
                # Adiciona novo ativo se não existir
                novo_item = {
                    "ticker": ticker,
                    "qtd": ativo['qtd'],
                    "preco_medio": ativo['preco_medio']
                }
                if is_fii:
                    novo_item["meta_cotas"] = None
                else:
                    novo_item["setor"] = "Não Definido"
                dados[lista_alvo].append(novo_item)
                
        with open('dados.json', 'w', encoding='utf-8') as f:
            json.dump(dados, f, indent=2, ensure_ascii=False)
            
        print("💾 Arquivo dados.json atualizado com sucesso!")
    except Exception as e:
        print(f"❌ Erro ao atualizar dados.json: {e}")

if __name__ == "__main__":
    print("🚀 Iniciando sincronização com Investidor 10...")
    sessao = login_investidor10()
    if sessao:
        ativos = extrair_ativos_carteira(sessao)
        if ativos:
            atualizar_dados_locais(ativos)
        else:
            print("⚠️ Nenhum ativo extraído. Verifique a estrutura da página.")
