import os
import json
import requests

# Lê o token e o repositório (formato: dono/repositorio)
GITHUB_TOKEN = os.getenv("GITHUB_TOKEN")
REPO = os.getenv("GITHUB_REPOSITORY")

# Lê o arquivo do evento para extrair o número do PR
with open("event.json", "r") as f:
    event_data = json.load(f)

pr_number = event_data["pull_request"]["number"]

# Lê o relatório
with open("analysis_report.txt", "r") as file:
    report = file.read()

# Envia o comentário para o PR
url = f"https://api.github.com/repos/{REPO}/issues/{pr_number}/comments"
headers = {
    "Authorization": f"Bearer {GITHUB_TOKEN}",
    "Content-Type": "application/json",
    "Accept": "application/vnd.github.v3+json"
}
data = {
    "body": f"## 🤖 Relatório de Análise de Código\n\n{report}"
}

response = requests.post(url, json=data, headers=headers)

if response.status_code == 201:
    print("✅ Comentário criado com sucesso!")
else:
    print(f"❌ Erro ao criar comentário: {response.status_code}")
    print(response.text)
