import os
import requests
from github import Github

# Configurações
HF_API_URL = "https://api-inference.huggingface.co/models/deepseek-ai/deepseek-coder-33b-instruct"
HF_TOKEN = os.getenv("HF_TOKEN")
GITHUB_TOKEN = os.getenv("GITHUB_TOKEN")
REPO_NAME = os.getenv("GITHUB_REPOSITORY")
PR_NUMBER = os.getenv("GITHUB_REF").split("/")[-2]

def get_diff():
    g = Github(GITHUB_TOKEN)
    repo = g.get_repo(REPO_NAME)
    pull_request = repo.get_pull(int(PR_NUMBER))
    
    # Obter diff completo
    return pull_request.get_files()

def analyze_with_ai(code_diff):
    headers = {"Authorization": f"Bearer {HF_TOKEN}"}
    
    prompt = """
    Analyze this code diff for:
    1. Potential bugs
    2. Security vulnerabilities
    3. Code smells
    4. Performance issues
    5. Style inconsistencies
    
    Return findings in this format:
    {
        "file": "filename",
        "line": number,
        "issue": "description",
        "severity": "low/medium/high",
        "suggestion": "how to fix"
    }
    
    Code diff:
    {code_diff}
    """
    
    response = requests.post(
        HF_API_URL,
        headers=headers,
        json={"inputs": prompt.format(code_diff=code_diff)}
    )
    
    return response.json()

def main():
    files = get_diff()
    findings = []
    
    for file in files:
        analysis = analyze_with_ai(file.patch)
        if isinstance(analysis, list):
            findings.extend(analysis)
        elif isinstance(analysis, dict):
            findings.append(analysis)
    
    # Salvar resultados para post_comments.py
    with open("findings.json", "w") as f:
        json.dump(findings, f)

if __name__ == "__main__":
    main()
