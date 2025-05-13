import os
import requests
import json
from github import Github

# Configurações da API
HF_API_URL = "https://api-inference.huggingface.co/models/deepseek-ai/deepseek-coder-33b-instruct"
HF_TOKEN = os.getenv("HF_TOKEN")
GITHUB_TOKEN = os.getenv("GITHUB_TOKEN")
REPO_NAME = os.getenv("GITHUB_REPOSITORY")
GITHUB_REF = os.getenv("GITHUB_REF", "refs/pull/1/merge")  # Valor padrão para testes

def get_pr_number():
    """Extrai o número da PR da referência do GitHub"""
    try:
        return int(GITHUB_REF.split('/')[2])
    except (IndexError, ValueError):
        return 1  # Valor padrão para testes locais

def get_diff():
    """Obtém os arquivos modificados na PR"""
    g = Github(GITHUB_TOKEN)
    repo = g.get_repo(REPO_NAME)
    return repo.get_pull(get_pr_number()).get_files()

def analyze_code_with_ai(code_diff, filename):
    """Envia o código para análise pela API da Hugging Face"""
    if not code_diff or not HF_TOKEN:
        return []
    
    headers = {"Authorization": f"Bearer {HF_TOKEN}"}
    
    prompt = f"""
    Analyze this code diff and identify potential issues:
    
    File: {filename}
    Diff:
    {code_diff}
    
    Return a JSON array with found issues, each with:
    - line: Line number
    - issue: Description of the issue
    - severity: low/medium/high
    - suggestion: How to fix it
    
    Example:
    [
        {{
            "line": 15,
            "issue": "Possible SQL injection",
            "severity": "high",
            "suggestion": "Use parameterized queries"
        }}
    ]
    """
    
    try:
        response = requests.post(
            HF_API_URL,
            headers=headers,
            json={"inputs": prompt},
            timeout=60
        )
        
        if response.status_code == 200:
            try:
                return response.json()
            except ValueError:
                print("Invalid JSON response from API")
        return []
    except Exception as e:
        print(f"API Error: {str(e)}")
        return []

def main():
    """Função principal de execução"""
    # Verifica variáveis de ambiente
    if not all([HF_TOKEN, GITHUB_TOKEN, REPO_NAME]):
        print("Variáveis de ambiente ausentes")
        return
    
    findings = []
    
    # Analisa cada arquivo modificado
    for file in get_diff():
        if file.patch:
            print(f"🔍 Analisando {file.filename}...")
            issues = analyze_code_with_ai(file.patch, file.filename)
            
            if issues and isinstance(issues, list):
                for issue in issues:
                    issue["file"] = file.filename
                    findings.append(issue)
    
    # Salva os resultados
    with open("findings.json", "w") as f:
        json.dump({"findings": findings}, f, indent=2)
    
    print(f"✅ Análise concluída. {len(findings)} problemas encontrados.")

if __name__ == "__main__":
    main()
