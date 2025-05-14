import os
import requests
import json
import time
import re
from github import Github

# Configurações
API_URL = "https://router.huggingface.co/hyperbolic/v1/chat/completions"
HF_TOKEN = "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"  # Seu token
MODEL_NAME = "deepseek-ai/DeepSeek-R1"
GITHUB_TOKEN = os.getenv("GITHUB_TOKEN")
REPO_NAME = os.getenv("GITHUB_REPOSITORY")

def obter_arquivos_pr():
    """Obtém os arquivos modificados na Pull Request"""
    g = Github(GITHUB_TOKEN)
    repo = g.get_repo(REPO_NAME)
    numero_pr = int(os.getenv("GITHUB_REF").split('/')[2])
    return repo.get_pull(numero_pr).get_files()

def extrair_json_da_resposta(conteudo):
    """Extrai o JSON da resposta do modelo, mesmo com texto adicional"""
    try:
        # Tenta encontrar um bloco JSON na resposta
        json_match = re.search(r'\[.*\]', conteudo, re.DOTALL)
        if json_match:
            return json.loads(json_match.group(0))
        return json.loads(conteudo)
    except json.JSONDecodeError:
        print(f"Não foi possível extrair JSON de: {conteudo}")
        return []

def analisar_com_ia(diff_codigo, nome_arquivo):
    """Analisa o código usando a API da Hugging Face"""
    headers = {
        "Authorization": f"Bearer {HF_TOKEN}",
        "Content-Type": "application/json"
    }
    
    mensagens = [
        {
            "role": "system",
            "content": "Você é um analisador de código rigoroso. Retorne APENAS um array JSON com problemas encontrados."
        },
        {
            "role": "user",
            "content": f"""Analise este diff de código Python para o arquivo: {nome_arquivo}

{diff_codigo}

Retorne um array JSON com o formato:
[
    {{
        "linha": <número>,
        "problema": "<descrição>",
        "gravidade": "alta/media/baixa",
        "sugestao": "<como_corrigir>"
    }}
]"""
        }
    ]

    tentativas_maximas = 3
    for tentativa in range(tentativas_maximas):
        try:
            resposta = requests.post(
                API_URL,
                headers=headers,
                json={
                    "messages": mensagens,
                    "model": MODEL_NAME,
                    "temperature": 0.1,
                    "response_format": {"type": "json_object"}
                },
                timeout=60
            )
            
            if resposta.status_code == 200:
                try:
                    resposta_chat = resposta.json()
                    conteudo = resposta_chat["choices"][0]["message"]["content"]
                    print(f"Resposta bruta da API: {conteudo}")  # Debug
                    return extrair_json_da_resposta(conteudo)
                except (KeyError, json.JSONDecodeError) as e:
                    print(f"Erro ao analisar resposta: {str(e)}")
                    return []
            
            print(f"Erro na API (tentativa {tentativa + 1}): {resposta.status_code} - {resposta.text}")
            time.sleep(2 ** tentativa)
            
        except requests.exceptions.RequestException as e:
            print(f"Falha na requisição (tentativa {tentativa + 1}): {str(e)}")
            time.sleep(2 ** tentativa)
    
    return []

def principal():
    """Função principal de execução"""
    problemas_encontrados = []
    
    try:
        arquivos = obter_arquivos_pr()
        for arquivo in arquivos:
            if arquivo.patch and arquivo.filename.endswith('.py'):
                print(f"🔍 Analisando {arquivo.filename}...")
                problemas = analisar_com_ia(arquivo.patch, arquivo.filename)
                
                if isinstance(problemas, list):
                    for problema in problemas:
                        if all(chave in problema for chave in ['linha', 'problema', 'gravidade', 'sugestao']):
                            problema['arquivo'] = arquivo.filename
                            problemas_encontrados.append(problema)
                            print(f"Problema encontrado: {problema}")
    except Exception as e:
        print(f"Erro na execução principal: {str(e)}")
    
    with open("findings.json", "w", encoding='utf-8') as f:
        json.dump({"problemas": problemas_encontrados}, f, indent=2, ensure_ascii=False)
    
    print(f"✅ Encontrados {len(problemas_encontrados)} problemas")

if __name__ == "__main__":
    principal()
