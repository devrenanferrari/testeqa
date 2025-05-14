import os
import json
from github import Github

# Configurações
CODEX_TOKEN = os.getenv("CODEX_TOKEN")
REPO_NAME = os.getenv("GITHUB_REPOSITORY")
PR_NUMBER = os.getenv("PR_NUMBER")  # Necessário definir no workflow ou extrair de GITHUB_REF

def carregar_findings():
    """Carrega os problemas encontrados a partir do arquivo findings.json"""
    try:
        with open("findings.json", "r", encoding='utf-8') as f:
            dados = json.load(f)
            return dados.get("problemas", [])
    except Exception as e:
        print(f"❌ Erro ao carregar findings.json: {str(e)}")
        return []

def postar_comentarios(problemas):
    """Posta comentários no pull request com base nos problemas encontrados"""
    if not CODEX_TOKEN:
        print("❌ Erro: CODEX_TOKEN não está configurado.")
        return
    
    if not PR_NUMBER:
        print("❌ Erro: PR_NUMBER não está configurado.")
        return
    
    try:
        g = Github(CODEX_TOKEN)
        repo = g.get_repo(REPO_NAME)
        pr = repo.get_pull(int(PR_NUMBER))
        
        if not problemas:
            pr.create_issue_comment("✅ Nenhum problema encontrado na análise de código!")
            print("ℹ️ Comentário de 'sem problemas' postado.")
            return
        
        comentario = "🔍 **Análise de Código Automática**\n\nForam encontrados os seguintes problemas:\n\n"
        for problema in problemas:
            comentario += f"- **Arquivo:** {problema['arquivo']}\n"
            comentario += f"  **Linha:** {problema['linha']}\n"
            comentario += f"  **Problema:** {problema['problema']} ({problema['gravidade']})\n"
            comentario += f"  **Sugestão:** {problema['sugestao']}\n\n"
        
        pr.create_issue_comment(comentario)
        print(f"✅ Comentário postado com {len(problemas)} problemas.")
    
    except Exception as e:
        print(f"❌ Erro ao postar comentários: {str(e)}")

def principal():
    """Função principal"""
    problemas = carregar_findings()
    postar_comentarios(problemas)

if __name__ == "__main__":
    principal()
