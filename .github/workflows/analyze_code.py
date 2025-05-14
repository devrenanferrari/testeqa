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
    try:
        g = Github(GITHUB_TOKEN)
        repo = g.get_repo(REPO_NAME)
        numero_pr = int(os.getenv("GITHUB_REF").split('/')[2])
        return repo.get_pull(numero_pr).get_files()
    except Exception as e:
        print(f"❌ Erro ao obter arquivos da PR: {str(e)}")
        return []

def extrair_json_da_resposta(conteudo):
    """Versão robusta para extrair JSON mesmo com texto adicional"""
    try:
        # Padrão para encontrar o JSON na resposta
        padrao_json = r'(\[\s*\{.*?\}\s*\])'
        match = re.search(padrao_json, conteudo, re.DOTALL)
        
        if match:
            json_str = match.group(1)
            # Remove caracteres problemáticos antes do parsing
            json_str = json_str.replace("\\n", "").replace("\\t", "")
            return json.loads(json_str)
        
        # Tenta parsear como JSON puro se não encontrar padrão
        return json.loads(conteudo)
    except json.JSONDecodeError as e:
        print(f"❌ Falha ao decodificar JSON: {str(e)}")
        print(f"Conteúdo problemático: {conteudo[:500]}...")  # Log parcial
        return []

def analisar_com_ia(diff_codigo, nome_arquivo):
    """Analisa o código usando IA com tratamento robusto de erros"""
    headers = {
        "Authorization": f"Bearer {HF_TOKEN}",
        "Content-Type": "application/json"
    }
    
    prompt = f"""Analise este código Python rigorosamente:

Arquivo: {nome_arquivo}
Diff:
{diff_codigo}

Identifique e retorne APENAS um array JSON com:
1. Vulnerabilidades de segurança (SQLi, XSS, etc.) - GRAVIDADE ALTA
2. Bugs e erros lógicos - GRAVIDADE MÉDIA
3. Más práticas de código - GRAVIDADE BAIXA

Formato exigido:
[
    {{
        "linha": <número>,
        "problema": "<descrição clara>",
        "gravidade": "alta/média/baixa",
        "sugestao": "<solução específica>"
    }}
]"""

    for tentativa in range(3):
        try:
            resposta = requests.post(
                API_URL,
                headers=headers,
                json={
                    "messages": [{
                        "role": "system",
                        "content": "Você é um analisador de código Python. Siga EXATAMENTE o formato solicitado."
                    }, {
                        "role": "user", 
                        "content": prompt
                    }],
                    "model": MODEL_NAME,
                    "temperature": 0.1,
                    "response_format": {"type": "json_object"}
                },
                timeout=45
            )

            if resposta.status_code == 200:
                dados = resposta.json()
                conteudo = dados["choices"][0]["message"]["content"]
                print(f"🔍 Resposta da API (tentativa {tentativa+1}): {conteudo[:200]}...")
                return extrair_json_da_resposta(conteudo)
            
            print(f"⚠️ Erro na API (tentativa {tentativa+1}): {resposta.status_code} - {resposta.text}")
            time.sleep(2 ** tentativa)
            
        except Exception as e:
            print(f"⚠️ Falha na requisição (tentativa {tentativa+1}): {str(e)}")
            time.sleep(2 ** tentativa)
    
    return []

def principal():
    """Função principal com tratamento completo de erros"""
    problemas = []
    
    try:
        arquivos = obter_arquivos_pr()
        if not arquivos:
            print("ℹ️ Nenhum arquivo modificado encontrado na PR")
            return

        for arquivo in arquivos:
            if not arquivo.patch:
                continue
                
            print(f"\n🔍 Analisando {arquivo.filename}...")
            resultado = analisar_com_ia(arquivo.patch, arquivo.filename)
            
            if isinstance(resultado, list):
                for item in resultado:
                    if all(k in item for k in ['linha', 'problema', 'gravidade', 'sugestao']):
                        item['arquivo'] = arquivo.filename
                        problemas.append(item)
                        print(f"   ✅ Problema: {item['problema']} (linha {item['linha']})")
            else:
                print(f"⚠️ Formato inválido de retorno para {arquivo.filename}")

    except Exception as e:
        print(f"❌ Erro crítico: {str(e)}")
    
    # Salva resultados mesmo com erros parciais
    with open("findings.json", "w", encoding='utf-8') as f:
        json.dump({"problemas": problemas}, f, indent=2, ensure_ascii=False)
    
    print(f"\n📊 Resultado final: {len(problemas)} problemas encontrados")

if __name__ == "__main__":
    principal()
