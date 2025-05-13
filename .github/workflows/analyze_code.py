import os
import requests
import json
import time
from github import Github

# Configurações
HF_API_URL = "https://api-inference.huggingface.co/models/deepseek-ai/deepseek-coder-33b-instruct"
HF_TOKEN = os.getenv("HF_TOKEN")
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
    
    prompt = f"""Analyze this code diff STRICTLY and report ALL issues:

File: {filename}
Diff:
{code_diff}

Identify:
1. Security issues (SQLi, XSS, command injection, etc.) - HIGH severity
2. Bugs and logical errors - MEDIUM severity
3. Code smells (duplication, bad practices) - LOW severity

Return VALID JSON array ONLY, example:
[
    {{
        "line": 10,
        "issue": "SQL injection vulnerability",
        "severity": "high",
        "suggestion": "Use parameterized queries"
    }}
]"""

    max_retries = 3
    for attempt in range(max_retries):
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
                except json.JSONDecodeError:
                    print(f"Invalid JSON response. Raw: {response.text}")
                    return []
            
            print(f"API Error (attempt {attempt + 1}): {response.status_code} - {response.text}")
            time.sleep(2 ** attempt)  # Backoff exponencial
            
        except requests.exceptions.RequestException as e:
            print(f"Request failed (attempt {attempt + 1}): {str(e)}")
            time.sleep(2 ** attempt)
    
    return []

def main():
    findings = []
    
    for file in get_pr_files():
        if file.patch and file.filename.endswith('.py'):  # Analisa apenas Python
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
