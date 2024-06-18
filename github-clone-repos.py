"""
Copyright Notice:

Author: Mathew Keeling
Date: 17 June 2024
"""

"""
Description: GitCloner

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

# Methods
def get_all_groups(GITLAB_URL:str) -> list:
    req = request.Request(f"{GITLAB_URL}/api/v4/groups?per_page=100", headers=headers)
    response = request.urlopen(req)
    return [group["full_path"] for group in json.loads(response.read())]

def get_subgroups(GITLAB_URL:str, group:str) -> list:
    req = request.Request(f"{GITLAB_URL}/api/v4/groups/{group}/subgroups?per_page=100", headers=headers)
    response = request.urlopen(req)
    return [subgroup["full_path"] for subgroup in json.loads(response.read())]

def get_projects_for_group(GITLAB_URL:str, group:str) -> list:
    # Handle Subgroups: Replace '/' with '%2F' in the group name
    if '/' in group:
        group = group.replace('/', '%2f')
    req = request.Request(f"{GITLAB_URL}/api/v4/groups/{group}/projects?per_page=100", headers=headers)
    response = request.urlopen(req)
    return [project["path_with_namespace"] for project in json.loads(response.read())]

def update_project(GITLAB_URL:str, project:str) -> None:
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
            os.system(f'cd {project} && git commit -m "GitCloner: {current_datetime}"')

            # Push changes to remote repository
            os.system(f"cd {project} && git remote set-url origin {GITLAB_URL_WITH_TOKEN}/{project}.git")
            os.system(f"cd {project} && git push origin {branch}")

        if project_info.get("archived"):
            # Skip commit and push for archived projects
            return

        # Store the GitLab username and password in the Git configuration
        os.system(f"cd {project} && git config credential.helper store && git config --global credential.helper store")

    else:
        # print that the project does not exist and clone it
        print(f"Repository {project} does not exist. Cloning...", flush=True)
        # Clone the project into a subdirectory under the group's name using the private key
        os.system(f"git clone {GITLAB_URL}/{project}.git {project}")


if __name__ == "__main__":
    # Set your GitLab instance URL and private token
    GITLAB_URL = "http://example-cn.example-ad.example-domain.local"
    GITLAB_FQDN = "example-cn.example-ad.example-domain.local"
    USER_NAME = "example-username"
    PRIVATE_TOKEN = "example-token"
    GITLAB_URL_WITH_TOKEN = f"http://{USER_NAME}:{PRIVATE_TOKEN}@{GITLAB_FQDN}"

    # Define the request headers
    headers = {
        "PRIVATE-TOKEN": PRIVATE_TOKEN
    }

    # Get all groups
    groups = get_all_groups(GITLAB_URL=GITLAB_URL)
    print("Debug: groups:     " + str(groups), flush=True)

    # Loop through each group
    for group in groups:
        # Create a directory for the group
        os.makedirs(group, exist_ok=True)

        # Get all projects in the group
        print("Debug: GITLAB_URL: " + GITLAB_URL, flush=True)
        print("Debug: group:      " + group, flush=True)
        print("Debug: request:    " + f"{GITLAB_URL}/api/v4/groups/{group}/projects?per_page=100)", flush=True)

        projects = get_projects_for_group(GITLAB_URL=GITLAB_URL, group=group)

        # Loop through each project
        for project in projects:
            print("Debug: project:    " + project, flush=True)
            update_project(GITLAB_URL=GITLAB_URL, project=project)
