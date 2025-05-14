import os
import json
from github import Github
from github.GithubException import GithubException

def load_findings():
    """Carrega os resultados da análise do arquivo JSON"""
    try:
        with open("findings.json", "r", encoding='utf-8') as f:
            data = json.load(f)
            return data.get("findings", [])
    except FileNotFoundError:
        print("❌ Error: findings.json not found")
    except json.JSONDecodeError:
        print("❌ Error: Invalid JSON format in findings.json")
    except Exception as e:
        print(f"❌ Unexpected error loading findings: {str(e)}")
    return []

def post_comments():
    findings = load_findings()
    
    if not findings:
        print("✅ No issues found to comment")
        return

    try:
        # Configuração do GitHub
        github_token = os.getenv("GITHUB_TOKEN")
        if not github_token:
            print("❌ GITHUB_TOKEN environment variable is missing")
            return

        repo_name = os.getenv("GITHUB_REPOSITORY")
        if not repo_name:
            print("❌ GITHUB_REPOSITORY environment variable is missing")
            return

        g = Github(github_token)
        repo = g.get_repo(repo_name)
        
        # Obtém o número da PR
        try:
            pr_ref = os.getenv("GITHUB_REF", "")
            pr_number = int(pr_ref.split('/')[2])
            pr = repo.get_pull(pr_number)
        except (IndexError, ValueError):
            print("❌ Could not determine PR number from GITHUB_REF")
            return
        
        # Posta os comentários
        posted_comments = 0
        for finding in findings:
            try:
                # Validação dos campos obrigatórios
                required_fields = ['issue', 'severity', 'suggestion', 'file', 'line']
                if not all(field in finding for field in required_fields):
                    print(f"⚠️ Skipping invalid finding: {finding}")
                    continue

                # Cria o comentário
                comment_body = (
                    f"🚨 **{finding['issue']}**\n\n"
                    f"📌 **Severity:** {finding['severity'].upper()}\n"
                    f"💡 **Suggestion:** {finding['suggestion']}\n"
                    f"🔗 **File:** {finding['file']}#L{finding['line']}"
                )

                pr.create_review_comment(
                    body=comment_body,
                    commit_id=pr.head.sha,
                    path=finding['file'],
                    line=finding['line'] or 1
                )
                posted_comments += 1
                
            except GithubException as ge:
                print(f"⚠️ GitHub API error for {finding.get('file', 'unknown')}: {str(ge)}")
            except Exception as e:
                print(f"⚠️ Error posting comment for {finding.get('file', 'unknown')}: {str(e)}")
        
        print(f"✅ Successfully posted {posted_comments}/{len(findings)} comments")
        
    except GithubException as ge:
        print(f"❌ GitHub API connection failed: {str(ge)}")
    except Exception as e:
        print(f"❌ Unexpected error: {str(e)}")

if __name__ == "__main__":
    post_comments()
