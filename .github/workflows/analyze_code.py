import os
import requests
import json
import time
from github import Github

# Configurações
API_URL = "https://router.huggingface.co/hyperbolic/v1/chat/completions"
HF_TOKEN = "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"  # Seu token
MODEL_NAME = "deepseek-ai/DeepSeek-R1"
GITHUB_TOKEN = os.getenv("GITHUB_TOKEN")
REPO_NAME = os.getenv("GITHUB_REPOSITORY")

def get_pr_files():
    g = Github(GITHUB_TOKEN)
    repo = g.get_repo(REPO_NAME)
    pr_number = int(os.getenv("GITHUB_REF").split('/')[2])
    return repo.get_pull(pr_number).get_files()

def analyze_with_ai(code_diff, filename):
    headers = {
        "Authorization": f"Bearer {HF_TOKEN}",
        "Content-Type": "application/json"
    }
    
    messages = [
        {
            "role": "system",
            "content": "You are a senior code reviewer. Analyze the code strictly and report all issues."
        },
        {
            "role": "user",
            "content": f"""Analyze this code diff for File: {filename}

{code_diff}

Identify:
1. Security issues (SQLi, XSS, command injection)
2. Bugs and logical errors
3. Code smells (duplication, bad practices)

Return ONLY valid JSON array in this format:
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
                    "temperature": 0.1  # Mais determinístico
                },
                timeout=60
            )
            
            if response.status_code == 200:
                try:
                    # Extrai o conteúdo JSON da resposta do chat
                    chat_response = response.json()
                    content = chat_response["choices"][0]["message"]["content"]
                    return json.loads(content)
                except (json.JSONDecodeError, KeyError) as e:
                    print(f"Failed to parse response: {str(e)}")
                    print(f"Raw response: {chat_response}")
                    return []
            
            print(f"API Error (attempt {attempt + 1}): {response.status_code} - {response.text}")
            time.sleep(2 ** attempt)
            
        except requests.exceptions.RequestException as e:
            print(f"Request failed (attempt {attempt + 1}): {str(e)}")
            time.sleep(2 ** attempt)
    
    return []

def main():
    findings = []
    
    for file in get_pr_files():
        if file.patch and file.filename.endswith('.py'):
            print(f"🔍 Analyzing {file.filename}...")
            issues = analyze_with_ai(file.patch, file.filename)
            
            if isinstance(issues, list):
                for issue in issues:
                    if all(key in issue for key in ['line', 'issue', 'severity', 'suggestion']):
                        issue['file'] = file.filename
                        findings.append(issue)
    
    with open("findings.json", "w") as f:
        json.dump({"findings": findings}, f, indent=2)
    
    print(f"✅ Found {len(findings)} issues")

if __name__ == "__main__":
    main()
