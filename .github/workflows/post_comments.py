import os
import json
from github import Github

def post_comments():
    GITHUB_TOKEN = os.getenv("GITHUB_TOKEN")
    REPO_NAME = os.getenv("GITHUB_REPOSITORY")
    PR_NUMBER = os.getenv("GITHUB_REF").split("/")[-2]
    
    g = Github(GITHUB_TOKEN)
    repo = g.get_repo(REPO_NAME)
    pr = repo.get_pull(int(PR_NUMBER))
    
    with open("findings.json", "r") as f:
        findings = json.load(f)
    
    for finding in findings:
        # Postar apenas issues médias/altas para não poluir
        if finding["severity"] in ["medium", "high"]:
            pr.create_review_comment(
                body=f"**{finding['issue']}** (Severity: {finding['severity']})\n\n"
                     f"Suggestion: {finding['suggestion']}",
                commit_id=pr.head.sha,
                path=finding["file"],
                line=finding["line"]
            )

if __name__ == "__main__":
    post_comments()
