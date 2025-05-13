import os
import json
from github import Github

def post_comments():
    try:
        with open("findings.json", "r") as f:
            data = json.load(f)
            findings = data.get("findings", [])
    except Exception as e:
        print(f"Error loading findings: {str(e)}")
        return

    if not findings:
        print("No issues to comment")
        return

    try:
        g = Github(os.getenv("GITHUB_TOKEN"))
        repo = g.get_repo(os.getenv("GITHUB_REPOSITORY"))
        pr = repo.get_pull(int(os.getenv("GITHUB_REF").split('/')[2]))
        
        for finding in findings:
            try:
                pr.create_review_comment(
                    body=f"🚨 **{finding['issue']}**\n"
                         f"📌 **Severity:** {finding['severity'].upper()}\n"
                         f"💡 **Suggestion:** {finding['suggestion']}",
                    commit_id=pr.head.sha,
                    path=finding['file'],
                    line=finding['line'] or 1  # Default para linha 1 se não especificado
                )
            except Exception as e:
                print(f"Failed to post comment for {finding['file']}: {str(e)}")
        
        print(f"Posted {len(findings)} comments successfully")
    except Exception as e:
        print(f"Failed to connect to GitHub: {str(e)}")

if __name__ == "__main__":
    post_comments()
