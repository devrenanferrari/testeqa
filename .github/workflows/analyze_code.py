import os
import requests
import json
from github import Github

HF_API_URL = "https://api-inference.huggingface.co/models/deepseek-ai/deepseek-coder-33b-instruct"
HF_TOKEN = os.getenv("HF_TOKEN")
GITHUB_TOKEN = os.getenv("GITHUB_TOKEN")
REPO_NAME = os.getenv("GITHUB_REPOSITORY")

def get_pr_files():
    g = Github(GITHUB_TOKEN)
    repo = g.get_repo(REPO_NAME)
    pr_number = int(os.getenv("GITHUB_REF").split('/')[2])
    return repo.get_pull(pr_number).get_files()

def analyze_code(file):
    headers = {"Authorization": f"Bearer {HF_TOKEN}"}
    
    # Prompt extremamente específico
    prompt = f"""ACT AS A SENIOR CODE REVIEWER. Analyze this code CRITICALLY:

File: {file.filename}
Code:
{file.patch}

Identify ALL issues including:
1. SECURITY vulnerabilities (SQLi, XSS, command injection, etc.) - MARK AS HIGH severity
2. BUGS and logical errors - MARK AS MEDIUM severity
3. CODE SMELLS (duplication, bad practices) - MARK AS LOW severity

RETURN ONLY VALID JSON ARRAY with format:
{{
  "line": <line_number>,
  "issue": "<description>",
  "severity": "<high/medium/low>",
  "suggestion": "<how_to_fix>"
}}

BE STRICT! Report ALL issues you find!"""

    try:
        response = requests.post(
            HF_API_URL,
            headers=headers,
            json={"inputs": prompt},
            timeout=30
        )
        return response.json()
    except Exception as e:
        print(f"Error analyzing {file.filename}: {str(e)}")
        return []

def main():
    findings = []
    for file in get_pr_files():
        if file.patch:
            print(f"🔍 Analyzing {file.filename}...")
            issues = analyze_code(file)
            if issues:
                for issue in issues:
                    issue["file"] = file.filename
                    findings.append(issue)
    
    with open("findings.json", "w") as f:
        json.dump({"findings": findings}, f, indent=2)
    
    print(f"✅ Found {len(findings)} issues")

if __name__ == "__main__":
    main()
