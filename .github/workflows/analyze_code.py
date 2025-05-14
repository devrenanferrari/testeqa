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

def get_pr_files():
    """Obtém os arquivos modificados na PR"""
    g = Github(GITHUB_TOKEN)
    repo = g.get_repo(REPO_NAME)
    pr_number = int(os.getenv("GITHUB_REF").split('/')[2])
    return repo.get_pull(pr_number).get_files()

def extract_json_from_response(content):
    """Extrai o JSON da resposta do modelo, mesmo com texto adicional"""
    try:
        # Tenta encontrar um bloco JSON na resposta
        json_match = re.search(r'\[.*\]', content, re.DOTALL)
        if json_match:
            return json.loads(json_match.group(0))
        return json.loads(content)
    except json.JSONDecodeError:
        print(f"Could not extract JSON from: {content}")
        return []

def analyze_with_ai(code_diff, filename):
    """Analisa o código usando a API da Hugging Face"""
    headers = {
        "Authorization": f"Bearer {HF_TOKEN}",
        "Content-Type": "application/json"
    }
    
    messages = [
        {
            "role": "system",
            "content": "You are a strict code reviewer. Return ONLY valid JSON array with found issues."
        },
        {
            "role": "user",
            "content": f"""Analyze this Python code diff for File: {filename}

{code_diff}

Return JSON array with format:
[
    {{
        "line": <number>,
        "issue": "<description>",
        "severity": "high/medium/low",
        "suggestion": "<how_to_fix>"
    }}
]"""
        }
    ]

    max_retries = 3
    for attempt in range(max_retries):
        try:
            response = requests.post(
                API_URL,
                headers=headers,
                json={
                    "messages": messages,
                    "model": MODEL_NAME,
                    "temperature": 0.1,
                    "response_format": {"type": "json_object"}
                },
                timeout=60
            )
            
            if response.status_code == 200:
                try:
                    chat_response = response.json()
                    content = chat_response["choices"][0]["message"]["content"]
                    print(f"Raw API response: {content}")  # Debug
                    return extract_json_from_response(content)
                except (KeyError, json.JSONDecodeError) as e:
                    print(f"Parse error: {str(e)}")
                    return []
            
            print(f"API Error (attempt {attempt + 1}): {response.status_code} - {response.text}")
            time.sleep(2 ** attempt)
            
        except requests.exceptions.RequestException as e:
            print(f"Request failed (attempt {attempt + 1}): {str(e)}")
            time.sleep(2 ** attempt)
    
    return []

def main():
    """Função principal"""
    findings = []
    
    try:
        files = get_pr_files()
        for file in files:
            if file.patch and file.filename.endswith('.py'):
                print(f"🔍 Analyzing {file.filename}...")
                issues = analyze_with_ai(file.patch, file.filename)
                
                if isinstance(issues, list):
                    for issue in issues:
                        if all(key in issue for key in ['line', 'issue', 'severity', 'suggestion']):
                            issue['file'] = file.filename
                            findings.append(issue)
                            print(f"Found issue: {issue}")
    except Exception as e:
        print(f"Error in main execution: {str(e)}")
    
    with open("findings.json", "w") as f:
        json.dump({"findings": findings}, f, indent=2)
    
    print(f"✅ Found {len(findings)} issues")

if __name__ == "__main__":
    main()
