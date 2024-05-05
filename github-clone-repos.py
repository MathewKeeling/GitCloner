"""
Copyright Notice:

Author: Mathew Keeling
Date: 05 May 2024
"""

"""
Description:

This script clones all GitLab repositories from a GitLab instance using the GitLab API.
It uses the GitLab API to get all groups and projects, then clones each project into a subdirectory under the group's name.
If the repository already exists, it performs a git pull to update the repository.
The script also commits and pushes changes to the remote repository if the project is not archived.
"""

import os
import json
from urllib import request
from getpass import getpass
from datetime import datetime

# Set your GitLab instance URL and private token
GITLAB_URL = "http://github.com"
GITLAB_FQDN = "github.com"
USER_NAME = "secretuser"
PRIVATE_TOKEN = "secrettoken"
GITLAB_URL_WITH_TOKEN = f"http://{USER_NAME}:{PRIVATE_TOKEN}@{GITLAB_FQDN}"

# Define the request headers
headers = {
    "PRIVATE-TOKEN": PRIVATE_TOKEN
}

# Get all groups
req = request.Request(f"{GITLAB_URL}/api/v4/groups?per_page=100", headers=headers)
response = request.urlopen(req)
groups = [group["full_path"] for group in json.loads(response.read())]

# Loop through each group
for group in groups:
    # Create a directory for the group
    os.makedirs(group, exist_ok=True)

    # Get all projects in the group
    req = request.Request(f"{GITLAB_URL}/api/v4/groups/{group}/projects?per_page=100", headers=headers)
    response = request.urlopen(req)
    projects = [project["path_with_namespace"] for project in json.loads(response.read())]

    # Loop through each project
    for project in projects:

        # Check if the repository already exists
        if os.path.exists(f"{project}"):

            # if a branch called master exists, define a variable for the branch name
            branch = "master" if os.path.exists(f"{project}/.git/refs/heads/master") else "main"
            print("Branch: ", branch, flush=True)

            # Print that the directory already exists.
            os.system(f"echo Repository {project} Already Exists! Performing git pull")
            # Execute a git pull to update the repository
            os.system(f"cd {project} && git pull {GITLAB_URL_WITH_TOKEN}/{project}.git {branch}")

            # Add all changes
            os.system(f"cd {project} && git add .")

            # Check if the project is archived
            req = request.Request(f"{GITLAB_URL}/api/v4/projects/{project.replace('/', '%2F')}", headers=headers)
            response = request.urlopen(req)
            project_info = json.loads(response.read())

            if not project_info.get("archived"):
                # Commit changes with current date and time
                current_datetime = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                os.system(f'cd {project} && git commit -m "{current_datetime}"')

                # Push changes to remote repository
                os.system(f"cd {project} && git remote set-url origin {GITLAB_URL_WITH_TOKEN}/{project}.git")
                os.system(f"cd {project} && git push origin {branch}")

            if project_info.get("archived"):
                # Skip commit and push for archived projects
                continue

            # Store the GitLab username and password in the Git configuration
            os.system(f"cd {project} && git config credential.helper store && git config --global credential.helper store")

        else:
            # print that the project does not exist and clone it
            print(f"Repository {project} does not exist. Cloning...", flush=True)
            # Clone the project into a subdirectory under the group's name using the private key
            os.system(f"git clone {GITLAB_URL}/{project}.git {project}")

