import os
import requests
from openai import OpenAI
from pathlib import Path

# Configurações
GITHUB_TOKEN = os.getenv("GITHUB_TOKEN")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
PR_NUMBER = os.getenv("PR_NUMBER")
REPO_NAME = os.getenv("REPO_NAME")

client = OpenAI(api_key=OPENAI_API_KEY)

def fetch_pr_diff():
    headers = {
        "Authorization": f"Bearer {GITHUB_TOKEN}",
        "Accept": "application/vnd.github.v3.diff"
    }
    url = f"https://api.github.com/repos/{REPO_NAME}/pulls/{PR_NUMBER}"
    response = requests.get(url, headers=headers)
    return response.text if response.status_code == 200 else None

def analyze_with_ai(diff):
    prompt = f"""
    Analise este diff de um Pull Request e:
    1. Identifique bugs, vulnerabilidades ou más práticas.
    2. Sugira melhorias (legibilidade, performance, etc.).
    3. Seja conciso e técnico.
    4. Inclua exemplos de código quando relevante.

    Diff:
    {diff[:8000]}
    """
    response = client.chat.completions.create(
        model="gpt-4-turbo",
        messages=[{"role": "user", "content": prompt}],
        max_tokens=1500
    )
    return response.choices[0].message.content

def save_feedback(feedback):
    Path("ai_feedback.md").write_text(feedback)

if __name__ == "__main__":
    diff = fetch_pr_diff()
    if diff:
        feedback = analyze_with_ai(diff)
        save_feedback(feedback)
        print("✅ Análise concluída! Feedback salvo em 'ai_feedback.md'.")
