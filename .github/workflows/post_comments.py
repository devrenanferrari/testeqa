import os
import json
from github import Github

def post_comments():
    with open("findings.json", "r") as f:
        findings = json.load(f).get("findings", [])
    
    if not findings:
        print("No issues found to comment")
        return
    
    g = Github(os.getenv("GITHUB_TOKEN"))
    repo = g.get_repo(os.getenv("GITHUB_REPOSITORY"))
    pr = repo.get_pull(int(os.getenv("GITHUB_REF").split('/')[2]))
    
    for finding in findings:
        pr.create_review_comment(
            body=f"🚨 **{finding['issue']}**\n"
                 f"📌 **Severity:** {finding['severity']}\n"
                 f"💡 **Suggestion:** {finding['suggestion']}",
            commit_id=pr.head.sha,
            path=finding["file"],
            line=finding["line"]
        )
    
    print(f"Posted {len(findings)} comments")

if __name__ == "__main__":
    post_comments()
