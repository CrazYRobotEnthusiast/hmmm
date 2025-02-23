import os
import requests
import base64
import subprocess
import json
from dotenv import load_dotenv
load_dotenv()

# GitHub Credentials
ACCESS_TOKEN = os.getenv("TOKEN")  # Replace with your token
GITHUB_USERNAME = "CrazYRobotEnthusiast"  # Replace with your username
REPO_NAME = "hmmm"  # Replace with your repo name
PARENT_DIRECTORY = "./"  # Path to the local directory containing files

GITHUB_API_URL = "https://api.github.com"

# GitHub API headers
HEADERS = {
    "Authorization": f"token {ACCESS_TOKEN}",
    "Accept": "application/vnd.github+json"
}

# Check if the repository already exists
repo_url = f"https://api.github.com/repos/{GITHUB_USERNAME}/{REPO_NAME}"
response = requests.get(repo_url, headers=HEADERS)

if response.status_code == 200:
    print(f"Repository '{REPO_NAME}' already exists. Skipping creation.")
else:
    print(f"Creating public repository '{REPO_NAME}' on GitHub...")
    create_repo_payload = {"name": REPO_NAME, "private": False}  # Ensure it's public
    create_response = requests.post(
        f"https://api.github.com/user/repos", headers=HEADERS, json=create_repo_payload
    )

    if create_response.status_code == 201:
        print(f"Repository '{REPO_NAME}' successfully created as public.")
    else:
        print(f"Failed to create repository: {create_response.json()}")
        exit(1)

# Initialize Git and set up the remote origin
os.chdir(PARENT_DIRECTORY)
subprocess.run(["git", "init"], check=True)
subprocess.run(["git", "branch", "-M", "main"], check=True)

# Add remote origin if not already set
result = subprocess.run(["git", "remote"], capture_output=True, text=True)
if "origin" not in result.stdout:
    subprocess.run(["git", "remote", "add", "origin", f"https://github.com/{GITHUB_USERNAME}/{REPO_NAME}.git"], check=True)
else:
    print("Remote 'origin' already exists. Skipping...")
def create_gh_pages_branch():
    """Create a gh-pages branch from main using the GitHub API."""
    url = f"{GITHUB_API_URL}/repos/{GITHUB_USERNAME}/{REPO_NAME}/git/refs/heads/gh-pages"
    response = requests.get(url, headers=HEADERS)

    if response.status_code == 200:
        print("gh-pages branch already exists. Skipping creation.")
        return

    url = f"{GITHUB_API_URL}/repos/{GITHUB_USERNAME}/{REPO_NAME}/git/refs/heads/main"
    response = requests.get(url, headers=HEADERS)

    if response.status_code == 200:
        sha = response.json()["object"]["sha"]
        data = {"ref": "refs/heads/gh-pages", "sha": sha}
        url = f"{GITHUB_API_URL}/repos/{GITHUB_USERNAME}/{REPO_NAME}/git/refs"
        response = requests.post(url, headers=HEADERS, json=data)

        if response.status_code == 201:
            print("gh-pages branch created successfully!")
        else:
            print(f"Failed to create gh-pages branch: {response.json()}")
    else:
        print(f"Failed to get main branch info: {response.json()}")



def enable_github_pages():
    """Enable GitHub Pages on gh-pages branch."""
    url = f"{GITHUB_API_URL}/repos/{GITHUB_USERNAME}/{REPO_NAME}/pages"
    data = {
        "source": {"branch": "gh-pages", "path": "/"},
    }
    response = requests.post(url, headers=HEADERS, json=data)
    if response.status_code == 201:
        print("GitHub Pages enabled!")
    else:
        print(f"Failed to enable GitHub Pages: {response.json()}")


def enable_workflow_permissions():
    """Enable read & write permissions for GitHub Actions workflows."""
    url = f"{GITHUB_API_URL}/repos/{GITHUB_USERNAME}/{REPO_NAME}/actions/permissions"
    data = {"enabled": True,  # Fix: Include "enabled" field
        "default_workflow_permissions": "write"}
    response = requests.put(url, headers=HEADERS, json=data)
    if response.status_code == 204:
        print("GitHub Actions workflows have read & write permissions!")
    else:
        print(f"Failed to enable workflow permissions: {response.json()}")

# Execute the steps
create_gh_pages_branch()
enable_github_pages()
enable_workflow_permissions()

subprocess.run(["git", "add", "."], check=True)
subprocess.run(["git", "commit", "-m", "Initial commit"], check=True)
subprocess.run(["git", "push", "-u", "origin", "main"], check=True)

print(f"Repository '{REPO_NAME}' created and pushed successfully.")