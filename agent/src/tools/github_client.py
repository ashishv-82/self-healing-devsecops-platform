import os
import requests
from typing import List, Dict, Any

GITHUB_TOKEN = os.getenv("GITHUB_TOKEN", "")
GITHUB_API_URL = "https://api.github.com"
REPO_OWNER = "ashishv-82" # Hardcoded for now, or fetch from alert tags
REPO_NAME = "self-healing-devsecops-platform"

def get_headers():
    return {
        "Authorization": f"Bearer {GITHUB_TOKEN}",
        "Accept": "application/vnd.github.v3+json"
    }

def get_recent_commits(service_name: str, limit: int = 5) -> List[Dict[str, Any]]:
    """
    Fetches recent commits for the repository.
    Ideally filters by path/service if monorepo support is added.
    """
    if not GITHUB_TOKEN or GITHUB_TOKEN == "your_token_here":
        print("⚠️ GITHUB_TOKEN not set. Returning mock data.")
        return [{
            "sha": "mock123",
            "message": f"Mock commit for {service_name}",
            "author": {"name": "Mock Dev", "email": "dev@example.com"},
            "date": "2024-01-01T12:00:00Z"
        }]

    url = f"{GITHUB_API_URL}/repos/{REPO_OWNER}/{REPO_NAME}/commits"
    params = {"per_page": limit}
    
    try:
        response = requests.get(url, headers=get_headers(), params=params)
        response.raise_for_status()
        
        commits = []
        for item in response.json():
            commit = {
                "sha": item['sha'],
                "message": item['commit']['message'],
                "author": item['commit']['author'],
                "date": item['commit']['author']['date']
            }
            commits.append(commit)
            
        print(f"✅ Fetched {len(commits)} commits from GitHub.")
        return commits

    except Exception as e:
        print(f"❌ Failed to fetch commits: {e}")
        return []

def create_revert_pr(commit_sha: str, reason: str) -> Dict[str, Any]:
    """
    Creates a Pull Request to revert a specific commit.
    This is a simplified implementation - in production, you'd:
    1. Create a new branch
    2. Cherry-pick the revert
    3. Create a PR
    """
    if not GITHUB_TOKEN or GITHUB_TOKEN == "your_token_here":
        print("⚠️ GITHUB_TOKEN not set. Returning mock PR.")
        return {
            "success": True,
            "pr_url": f"https://github.com/{REPO_OWNER}/{REPO_NAME}/pull/mock-123",
            "message": f"[MOCK] Would create revert PR for commit {commit_sha}"
        }

    # Step 1: Get the commit to revert
    commit_url = f"{GITHUB_API_URL}/repos/{REPO_OWNER}/{REPO_NAME}/commits/{commit_sha}"
    try:
        commit_response = requests.get(commit_url, headers=get_headers())
        commit_response.raise_for_status()
        commit_data = commit_response.json()
        commit_message = commit_data['commit']['message'].split('\n')[0]
    except Exception as e:
        print(f"❌ Failed to fetch commit details: {e}")
        return {"success": False, "message": str(e)}

    # Step 2: Create a new branch for the revert
    branch_name = f"agent/revert-{commit_sha[:7]}"
    
    # Get default branch SHA
    try:
        refs_url = f"{GITHUB_API_URL}/repos/{REPO_OWNER}/{REPO_NAME}/git/refs/heads/main"
        refs_response = requests.get(refs_url, headers=get_headers())
        refs_response.raise_for_status()
        base_sha = refs_response.json()['object']['sha']
    except Exception as e:
        print(f"❌ Failed to get base branch: {e}")
        return {"success": False, "message": str(e)}

    # Create branch
    try:
        create_ref_url = f"{GITHUB_API_URL}/repos/{REPO_OWNER}/{REPO_NAME}/git/refs"
        create_ref_payload = {
            "ref": f"refs/heads/{branch_name}",
            "sha": base_sha
        }
        requests.post(create_ref_url, headers=get_headers(), json=create_ref_payload)
    except Exception as e:
        print(f"⚠️ Branch might already exist: {e}")

    # Step 3: Create Pull Request
    pr_url = f"{GITHUB_API_URL}/repos/{REPO_OWNER}/{REPO_NAME}/pulls"
    pr_payload = {
        "title": f"[Agent] Revert: {commit_message}",
        "body": f"""## Automated Revert by Self-Healing Agent

**Reason:** {reason}

**Reverted Commit:** {commit_sha}

---
*This PR was created automatically by the Self-Healing DevSecOps Agent.*
""",
        "head": branch_name,
        "base": "main"
    }
    
    try:
        pr_response = requests.post(pr_url, headers=get_headers(), json=pr_payload)
        pr_response.raise_for_status()
        pr_data = pr_response.json()
        
        print(f"✅ Created revert PR: {pr_data['html_url']}")
        return {
            "success": True,
            "pr_url": pr_data['html_url'],
            "pr_number": pr_data['number'],
            "message": f"Created PR #{pr_data['number']} to revert {commit_sha[:7]}"
        }
    except Exception as e:
        print(f"❌ Failed to create PR: {e}")
        return {"success": False, "message": str(e)}

if __name__ == "__main__":
    # Test execution
    print("Testing GitHub Client...")
    commits = get_recent_commits("frontend")
    print(commits)
