import os
import requests
import json
from github import Github

# Configuration
HF_API_URL = "https://api-inference.huggingface.co/models/deepseek-ai/deepseek-coder-33b-instruct"
HF_TOKEN = os.getenv("HF_TOKEN")
GITHUB_TOKEN = os.getenv("GITHUB_TOKEN")
REPO_NAME = os.getenv("GITHUB_REPOSITORY")
GITHUB_REF = os.getenv("GITHUB_REF", "refs/pull/1/merge")

def get_pr_number():
    """Extract PR number from GITHUB_REF"""
    try:
        return int(GITHUB_REF.split('/')[2])
    except (IndexError, ValueError):
        return 1  # Default for local testing

def get_diff():
    """Get PR diff files"""
    g = Github(GITHUB_TOKEN)
    repo = g.get_repo(REPO_NAME)
    return repo.get_pull(get_pr_number()).get_files()

def build_prompt(code_diff):
    """Build the analysis prompt without any string formatting"""
    example = {
        "issues": [{
            "file": "example.py",
            "line": 10,
            "issue": "Potential null reference",
            "severity": "medium",
            "suggestion": "Add null check"
        }]
    }
    
    return [
        "Analyze this code diff for:",
        "1. Bugs and logical errors",
        "2. Security vulnerabilities",
        "3. Code smells",
        "4. Performance issues",
        "5. Style inconsistencies",
        "",
        f"Return findings in JSON format like this: {json.dumps(example)}",
        "",
        "Code diff to analyze:",
        code_diff
    ]

def analyze_with_ai(code_diff):
    """Send code to AI for analysis"""
    if not code_diff or not HF_TOKEN:
        return []
    
    headers = {"Authorization": f"Bearer {HF_TOKEN}"}
    prompt_lines = build_prompt(code_diff)
    prompt_text = "\n".join(prompt_lines)
    
    try:
        response = requests.post(
            HF_API_URL,
            headers=headers,
            json={"inputs": prompt_text},
            timeout=60
        )
        return response.json().get("issues", []) if response.ok else []
    except Exception as e:
        print(f"Analysis failed: {e}")
        return []

def main():
    """Main execution"""
    # Verify environment
    if not all([HF_TOKEN, GITHUB_TOKEN, REPO_NAME]):
        print("Missing required environment variables")
        return
    
    # Process files
    findings = []
    for file in get_diff():
        if file.patch:
            print(f"Analyzing {file.filename}...")
            for issue in analyze_with_ai(file.patch):
                issue["file"] = file.filename
                findings.append(issue)
    
    # Save results
    with open("findings.json", "w") as f:
        json.dump({"findings": findings}, f, indent=2)
    
    print(f"Found {len(findings)} issues")

if __name__ == "__main__":
    main()
