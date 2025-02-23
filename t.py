import subprocess
import requests
import os

# GitHub hmmm
REPO_NAME = "hmmm"
OWNER = "CrazYRobotEnthusiast"
GITHUB_TOKEN = os.environ.get("TOKEN")  # Store your GitHub token in environment variables

# GitHub API headers
HEADERS = {
    "Authorization": f"Bearer {GITHUB_TOKEN}",
    "Accept": "application/vnd.github+json"
}

# Check if the repository already exists
repo_url = f"https://api.github.com/repos/{OWNER}/{REPO_NAME}"
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
pages_url = f"https://api.github.com/repos/{OWNER}/{REPO_NAME}/pages"
pages_payload = {"source": {"branch": "gh-pages", "path": "/"}}
response = requests.post(pages_url, headers=HEADERS, json=pages_payload)

if response.status_code in [200, 201, 202]:
    print("GitHub Pages enabled from 'gh-pages' branch")
else:
    print(f"Failed to enable GitHub Pages: {response.json()}")

print(f"Repository '{REPO_NAME}' created and deployed at: https://{OWNER}.github.io/{REPO_NAME}")
