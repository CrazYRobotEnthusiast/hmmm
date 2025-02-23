import subprocess
import requests
import os

# GitHub Repository Info
REPO_NAME = "hmmm"
OWNER = "CrazYRobotEnthusiast"
GITHUB_TOKEN = os.environ.get("TOKEN")  # Store your GitHub token in environment variables
GITHUB_API_URL = "https://api.github.com"

# GitHub API headers
HEADERS = {
    "Authorization": f"token {GITHUB_TOKEN}",
    "Accept": "application/vnd.github+json"
}

# Function to enable workflow permissions
def enable_workflow_permissions():
    """Enable read & write permissions for GitHub Actions workflows."""
    url = f"{GITHUB_API_URL}/repos/{OWNER}/{REPO_NAME}/actions/permissions"
    data = {"enabled": True, "allowed_actions": "all"}
    response = requests.put(url, headers=HEADERS, json=data)
    if response.status_code == 204:
        print("GitHub Actions workflows have read & write permissions!")
    else:
        print(f"Failed to enable workflow permissions: {response.json()}")

# Check if the repository already exists
repo_url = f"{GITHUB_API_URL}/repos/{OWNER}/{REPO_NAME}"
response = requests.get(repo_url, headers=HEADERS)

if response.status_code == 200:
    print(f"Repository '{REPO_NAME}' already exists. Skipping creation.")
else:
    print(f"Creating repository '{REPO_NAME}' on GitHub...")
    subprocess.run(["gh", "repo", "create", REPO_NAME, "--public"], check=False)

# Initialize Git
subprocess.run(["git", "init"], check=True)
subprocess.run(["git", "branch", "-M", "main"], check=True)

# Check if remote exists
remote_check = subprocess.run(["git", "remote"], capture_output=True, text=True)
if "origin" not in remote_check.stdout:
    subprocess.run(["git", "remote", "add", "origin", f"https://github.com/{OWNER}/{REPO_NAME}.git"], check=True)
else:
    print("Remote 'origin' already exists. Skipping...")

# Ensure .env is in .gitignore
gitignore_path = ".gitignore"
if not os.path.exists(gitignore_path) or ".env" not in open(gitignore_path).read():
    with open(gitignore_path, "a") as f:
        f.write("\n.env\n")
    subprocess.run(["git", "add", ".gitignore"], check=True)

# Add and commit changes if necessary
status_output = subprocess.run(["git", "status", "--porcelain"], capture_output=True, text=True)
if status_output.stdout.strip():
    subprocess.run(["git", "add", "."], check=True)
    subprocess.run(["git", "commit", "-m", "Initial commit"], check=True)
else:
    print("No changes to commit. Skipping commit step.")

# Push main branch
subprocess.run(["git", "push", "-u", "origin", "main"], check=True)

# Create & push gh-pages branch
subprocess.run(["git", "checkout", "--orphan", "gh-pages"], check=True)
subprocess.run(["git", "commit", "--allow-empty", "-m", "Initial commit for GitHub Pages"], check=True)
subprocess.run(["git", "push", "-u", "origin", "gh-pages"], check=True)

# Enable GitHub Pages
pages_url = f"{GITHUB_API_URL}/repos/{OWNER}/{REPO_NAME}/pages"
pages_payload = {"build_type":"workflow","source": {"branch": "gh-pages", "path": "/"}}
response = requests.post(pages_url, headers=HEADERS, json=pages_payload)

if response.status_code in [200, 201, 202]:
    print("GitHub Pages enabled from 'gh-pages' branch")
else:
    print(f"Failed to enable GitHub Pages: {response.json()}")

# Enable workflow permissions
enable_workflow_permissions()

print(f"Repository '{REPO_NAME}' created and deployed at: https://{OWNER}.github.io/{REPO_NAME}")