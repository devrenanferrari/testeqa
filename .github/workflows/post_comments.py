import os
import json
from github import Github
from github.GithubException import GithubException

def carregar_resultados():
    """Carrega os resultados da análise do arquivo JSON"""
    try:
        with open("findings.json", "r", encoding='utf-8') as f:
            dados = json.load(f)
            return dados.get("problemas", [])  # Agora usando "problemas" em vez de "findings"
    except FileNotFoundError:
        print("❌ Erro: Arquivo findings.json não encontrado")
    except json.JSONDecodeError:
        print("❌ Erro: Formato JSON inválido no arquivo findings.json")
    except Exception as e:
        print(f"❌ Erro inesperado ao carregar resultados: {str(e)}")
    return []

def postar_comentarios():
    problemas = carregar_resultados()
    
    if not problemas:
        print("✅ Nenhum problema encontrado para comentar")
        return

    try:
        # Configuração do GitHub
        token_github = os.getenv("GITHUB_TOKEN")
        if not token_github:
            print("❌ Variável de ambiente GITHUB_TOKEN não encontrada")
            return

        nome_repositorio = os.getenv("GITHUB_REPOSITORY")
        if not nome_repositorio:
            print("❌ Variável de ambiente GITHUB_REPOSITORY não encontrada")
            return

        g = Github(token_github)
        repositorio = g.get_repo(nome_repositorio)

        # Obtém o número da PR
        try:
            referencia_pr = os.getenv("GITHUB_REF", "")
            numero_pr = int(referencia_pr.split('/')[2])
            pr = repositorio.get_pull(numero_pr)
        except (IndexError, ValueError):
            print("❌ Não foi possível obter o número da PR a partir de GITHUB_REF")
            return

        comentarios_postados = 0
        for problema in problemas:
            try:
                # Validação dos campos obrigatórios
                campos_obrigatorios = ['problema', 'gravidade', 'sugestao', 'arquivo', 'linha']
                if not all(campo in problema for campo in campos_obrigatorios):
                    print(f"⚠️ Pulando problema inválido: {problema}")
                    continue

                # Cria o corpo do comentário
                corpo_comentario = (
                    f"🤖 **Análise Automática de Código**\n\n"
                    f"🚨 **Problema:** {problema['problema']}\n"
                    f"⚠️ **Gravidade:** {problema['gravidade'].upper()}\n"
                    f"💡 **Sugestão:** {problema['sugestao']}\n"
                    f"📂 **Arquivo:** `{problema['arquivo']}` Linha `{problema['linha']}`"
                )

                # Posta como comentário geral na PR
                pr.create_issue_comment(corpo_comentario)
                comentarios_postados += 1

            except GithubException as ge:
                print(f"⚠️ Erro na API do GitHub para {problema.get('arquivo', 'desconhecido')}: {str(ge)}")
            except Exception as e:
                print(f"⚠️ Erro ao postar comentário para {problema.get('arquivo', 'desconhecido')}: {str(e)}")
        
        print(f"✅ {comentarios_postados}/{len(problemas)} comentários postados com sucesso")
        
    except GithubException as ge:
        print(f"❌ Falha na conexão com a API do GitHub: {str(ge)}")
    except Exception as e:
        print(f"❌ Erro inesperado: {str(e)}")

if __name__ == "__main__":
    postar_comentarios()
