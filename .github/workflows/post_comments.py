import os
import requests
import json

GITHUB_TOKEN = os.getenv("GITHUB_TOKEN")
EVENT_PATH = os.getenv("GITHUB_EVENT_PATH")

# Carrega o número do PR a partir do arquivo de evento
with open(EVENT_PATH, "r") as f:
    event = json.load(f)
    pr_number = event["pull_request"]["number"]
    repo_full = event["repository"]["full_name"]

# Lê o relatório gerado
with open("analysis_report.txt", "r") as file:
    report = file.read()

# URL da API para criar comentários no PR
url = f"https://api.github.com/repos/{repo_full}/issues/{pr_number}/comments"

# Dados do comentário
data = {
    "body": f"## 🤖 Relatório de Análise de Código Automática\n\n```\n{report}\n```"
}

# Cabeçalhos da requisição
headers = {
    "Authorization": f"Bearer {GITHUB_TOKEN}",
    "Content-Type": "application/json"
}

# Faz a requisição para criar o comentário
response = requests.post(url, json=data, headers=headers)

if response.status_code == 201:
    print("✅ Comentário criado com sucesso!")
else:
    print(f"❌ Erro ao criar comentário: {response.status_code}")
    print(response.text)
