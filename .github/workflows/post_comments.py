import os
import requests
from pathlib import Path

# Configurações
GITHUB_TOKEN = os.getenv("GITHUB_TOKEN")
PR_NUMBER = os.getenv("PR_NUMBER")
REPO_NAME = os.getenv("REPO_NAME")

def post_feedback_to_pr():
    """Posta o feedback da OpenAI como comentário no PR."""
    feedback = Path("ai_feedback.md").read_text()
    headers = {
        "Authorization": f"Bearer {GITHUB_TOKEN}",
        "Accept": "application/vnd.github.v3+json"
    }
    payload = {
        "body": f"## 🤖 Análise Automática de Código\n\n{feedback}"
    }
    url = f"https://api.github.com/repos/{REPO_NAME}/issues/{PR_NUMBER}/comments"
    response = requests.post(url, headers=headers, json=payload)
    print(f"✅ Comentário postado! Status: {response.status_code}" if response.status_code == 201 else f"❌ Erro: {response.status_code}")

if __name__ == "__main__":
    post_feedback_to_pr()
