import os
import json
import requests

# Carrega token e repositório
GITHUB_TOKEN = os.getenv("GITHUB_TOKEN")
REPO = os.getenv("GITHUB_REPOSITORY")  # Formato: "owner/repo"

# Carrega o evento do GitHub Actions
with open("event.json", "r") as f:
    event_data = json.load(f)

# Extrai o número da PR
pr_number = event_data["pull_request"]["number"]

# Lê o relatório gerado
with open("analysis_report.txt", "r") as file:
    report = file.read()

# Prepara a requisição
url = f"https://api.github.com/repos/{REPO}/issues/{pr_number}/comments"
headers = {
    "Authorization": f"Bearer {GITHUB_TOKEN}",
    "Content-Type": "application/json",
    "Accept": "application/vnd.github.v3+json"
}
data = {
    "body": f"## 🤖 Relatório de Análise de Código\n\n{report}"
}

# Envia o comentário
response = requests.post(url, json=data, headers=headers)

# Feedback
if response.status_code == 201:
    print("✅ Comentário criado com sucesso!")
else:
    print(f"❌ Erro ao criar comentário: {response.status_code}")
    print(response.text)
