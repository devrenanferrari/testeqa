import os
import json
from github import Github

def post_comments():
    """Posta comentários na PR baseado nos resultados da análise"""
    # Configurações
    GITHUB_TOKEN = os.getenv("GITHUB_TOKEN")
    REPO_NAME = os.getenv("GITHUB_REPOSITORY")
    GITHUB_REF = os.getenv("GITHUB_REF", "refs/pull/1/merge")
    
    # Carrega os resultados da análise
    try:
        with open("findings.json", "r") as f:
            data = json.load(f)
            findings = data.get("findings", [])
    except FileNotFoundError:
        print("Arquivo findings.json não encontrado")
        return
    except json.JSONDecodeError:
        print("Erro ao ler findings.json")
        return
    
    if not findings:
        print("Nenhum problema encontrado para comentar")
        return
    
    try:
        # Configuração do GitHub
        g = Github(GITHUB_TOKEN)
        repo = g.get_repo(REPO_NAME)
        pr_number = int(GITHUB_REF.split('/')[2])
        pr = repo.get_pull(pr_number)
        
        # Posta cada comentário
        for finding in findings:
            if isinstance(finding, dict):
                severity = finding.get("severity", "low").lower()
                
                if severity in ["medium", "high"]:
                    comment_body = (
                        f"**{finding.get('issue', 'Problema encontrado')}**\n\n"
                        f"**Severidade:** {severity}\n"
                        f"**Sugestão:** {finding.get('suggestion', 'Revise este código')}\n"
                        f"**Arquivo:** {finding.get('file', '')}"
                    )
                    
                    pr.create_review_comment(
                        body=comment_body,
                        commit_id=pr.head.sha,
                        path=finding.get("file", ""),
                        line=finding.get("line", 1)
                    )
        
        print("💬 Comentários postados com sucesso na PR")
    except Exception as e:
        print(f"❌ Falha ao postar comentários: {str(e)}")

if __name__ == "__main__":
    post_comments()
