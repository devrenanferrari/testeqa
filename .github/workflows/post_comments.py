import os
import requests

GITHUB_TOKEN = os.getenv("GITHUB_TOKEN")
REPO_OWNER = "devrenanferrari"  # Substitua pelo seu usuário no GitHub
REPO_NAME = "testeqa"  # Substitua pelo nome do seu repositório
PR_NUMBER = os.getenv("GITHUB_REF").split("/")[-1]  # Pega o número do PR a partir do contexto do GitHub Action

# Lê o relatório gerado
with open("analysis_report.txt", "r") as file:
    report = file.read()

# URL da API para criar comentários no PR
url = f"https://api.github.com/repos/{REPO_OWNER}/{REPO_NAME}/issues/{PR_NUMBER}/comments"

# Dados do comentário
data = {
    "body": f"## Relatório de Análise de Código\n\n{report}"
}

# Cabeçalhos da requisição
headers = {
    "Authorization": f"Bearer {GITHUB_TOKEN}",
    "Content-Type": "application/json"
}

# Faz a requisição para criar o comentário
response = requests.post(url, json=data, headers=headers)

if response.status_code == 201:
    print("Comentário criado com sucesso!")
else:
    print(f"Erro ao criar comentário: {response.status_code}")
    print(response.text)
