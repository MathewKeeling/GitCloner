"""
Copyright Notice:

Author: Mathew Keeling
Date: 21 October 2024

Description: git_helper

This script automates the cloning of all GitLab repositories from a specified GitLab 
instance using the GitLab API. It retrieves all groups and projects, then clones each 
project into a subdirectory named after the group. If a repository already exists locally, 
the script performs a `git pull` to update it. Additionally, the script commits and pushes 
any changes to the remote repository, provided the project is not archived.
"""

import os
import json
import logging
from urllib import request, error
from datetime import datetime
import argparse
import configparser


class git_helper:
    """
    A class to clone and update GitLab repositories.

    Attributes:
        gitlab_url (str): The URL of the GitLab instance.
        user (str): The GitLab username.
        private_token (str): The GitLab private token.
        verbose (bool): Flag to enable verbose logging.

    Methods:
        setup_logging(): Sets up logging configuration.
        get_all_groups(): Retrieves all groups from the GitLab instance.
        get_projects_for_group(group): Retrieves all projects for a given group.
        get_subgroups_for_group(group): Retrieves all subgroups for a given group.
        display_groups_and_projects(): Displays all groups and their projects.
        update_project(project): Updates a given project by pulling the latest changes.
        clone_selected_repositories(selected_projects): Clones selected repositories.
        clone_selected_groups(selected_groups): Clones selected groups and their projects.
        clone_group_recursively(group): Recursively clones a group and its subgroups.
        clone_all(): Clones all groups and their projects.
    """
    def __init__(self, gitlab_url, user, private_token, verbose=False):
        self.gitlab_url = gitlab_url
        self.user = user
        self.private_token = private_token
        self.headers = {"PRIVATE-TOKEN": private_token}
        self.gitlab_url_with_token = (
            f"https://{user}:{private_token}@{gitlab_url.lstrip('https://')}"
        )
        self.verbose = verbose
        self.setup_logging()

    def setup_logging(self):
        logging.basicConfig(
            filename="git_helper.log",
            level=logging.DEBUG if self.verbose else logging.INFO,
            format="%(asctime)s - %(levelname)s - %(message)s",
        )
        self.logger = logging.getLogger()

    def get_all_groups(self):
        try:
            req = request.Request(
                f"{self.gitlab_url}/api/v4/groups?per_page=100", headers=self.headers
            )
            response = request.urlopen(req)
            groups = json.loads(response.read())
            return [group["full_path"] for group in groups]
        except error.URLError as e:
            self.logger.error(f"Network error: {e}")
            return []
        except Exception as e:
            self.logger.error(f"Error fetching groups: {e}")
            return []

    def get_projects_for_group(self, group):
        try:
            if "/" in group:
                group = group.replace("/", "%2f")
            req = request.Request(
                f"{self.gitlab_url}/api/v4/groups/{group}/projects?per_page=100",
                headers=self.headers,
            )
            response = request.urlopen(req)
            projects = json.loads(response.read())
            return [project["path_with_namespace"] for project in projects]
        except error.URLError as e:
            self.logger.error(f"Network error: {e}")
            return []
        except Exception as e:
            self.logger.error(f"Error fetching projects for group {group}: {e}")
            return []

    def get_subgroups_for_group(self, group):
        try:
            if "/" in group:
                group = group.replace("/", "%2f")
            req = request.Request(
                f"{self.gitlab_url}/api/v4/groups/{group}/subgroups?per_page=100",
                headers=self.headers,
            )
            response = request.urlopen(req)
            subgroups = json.loads(response.read())
            return [subgroup["full_path"] for subgroup in subgroups]
        except error.URLError as e:
            self.logger.error(f"Network error: {e}")
            return []
        except Exception as e:
            self.logger.error(f"Error fetching subgroups for group {group}: {e}")
            return []

    def display_groups_and_projects(self):
        groups = self.get_all_groups()
        group_project_map = {}
        for group in groups:
            projects = self.get_projects_for_group(group)
            group_project_map[group] = projects
        return group_project_map

    def update_project(self, project):
        try:
            self.logger.info(f"Processing project: {project}")
            if os.path.exists(f"{project}"):
                branch = (
                    "master"
                    if os.path.exists(f"{project}/.git/refs/heads/master")
                    else "main"
                )
                self.logger.info(f"Branch: {branch}")
                self.logger.info(
                    f"Repository {project} already exists. Performing git pull..."
                )
                os.system(
                    f"cd {project} && git pull {self.gitlab_url_with_token}/{project}.git {branch}"
                )
                os.system(f"cd {project} && git add .")

                req = request.Request(
                    f"{self.gitlab_url}/api/v4/projects/{project.replace('/', '%2F')}",
                    headers=self.headers,
                )
                response = request.urlopen(req)
                project_info = json.loads(response.read())

                if not project_info.get("archived"):
                    current_datetime = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                    os.system(
                        f'cd {project} && git commit -m "git_helper: {current_datetime}"'
                    )
                    os.system(
                        f"cd {project} && git remote set-url origin {self.gitlab_url}/{project}.git"
                    )
                    os.system(f"cd {project} && git push origin {branch}")

                if project_info.get("archived"):
                    self.logger.info(f"Project {project} is archived. Skipping...")
                    return

                os.system(
                    f"cd {project} && git config credential.helper store && git config --global credential.helper store"
                )
            else:
                self.logger.info(f"Repository {project} does not exist. Cloning...")
                os.system(
                    f"git clone {self.gitlab_url_with_token}/{project}.git {project}"
                )
        except Exception as e:
            self.logger.error(f"Error updating project {project}: {e}")

    def clone_selected_repositories(self, selected_projects):
        for project in selected_projects:
            self.update_project(project)

    def clone_selected_groups(self, selected_groups):
        for group in selected_groups:
            self.clone_group_recursively(group)

    def clone_group_recursively(self, group):
        projects = self.get_projects_for_group(group)
        for project in projects:
            self.update_project(project)

        subgroups = self.get_subgroups_for_group(group)
        for subgroup in subgroups:
            self.clone_group_recursively(subgroup)

    def clone_all(self):
        groups = self.get_all_groups()
        for group in groups:
            self.clone_group_recursively(group)


def create_config_file():
    config = configparser.ConfigParser()
    config["gitlab"] = {
        "url": "https://your-gitlab-url",
        "user": "your-username",
        "private_token": "your-private-token",
    }
    with open("git_helper.ini", "w") as configfile:
        config.write(configfile)
    print("Configuration file 'git_helper.ini' created with generic values.")
    print("Please update it with your GitLab URL, username, and private token.")
    print("Exiting...")


if __name__ == "__main__":
    if not os.path.exists("git_helper.ini"):
        create_config_file()
        exit(1)

    config = configparser.ConfigParser()
    config.read("git_helper.ini")

    GITLAB_URL = config["gitlab"]["url"]
    USER = config["gitlab"]["user"]
    PRIVATE_TOKEN = config["gitlab"]["private_token"]

    parser = argparse.ArgumentParser(
        description="Clone and update GitLab repositories."
    )
    parser.add_argument(
        "--projects", type=str, help="Comma-separated list of projects to clone."
    )
    parser.add_argument(
        "--groups", type=str, help="Comma-separated list of groups to clone."
    )
    parser.add_argument(
        "--all", action="store_true", help="Clone all projects from all groups."
    )
    parser.add_argument(
        "-v", "--verbose", action="store_true", help="Enable verbose logging."
    )
    args = parser.parse_args()

    cloner = git_helper(GITLAB_URL, USER, PRIVATE_TOKEN, verbose=args.verbose)

    if args.all:
        cloner.clone_all()
    elif args.projects:
        projects = args.projects.split(",")
        cloner.clone_selected_repositories(projects)
    elif args.groups:
        groups = args.groups.split(",")
        cloner.clone_selected_groups(groups)
    else:
        # Default to user prompts if no arguments are provided
        group_project_map = cloner.display_groups_and_projects()
        for group, projects in group_project_map.items():
            print(f"\nGroup: {group}")
            for project in projects:
                print(f"  Project: {project}")

        choice = (
            input(
                "\nWould you like to clone and update a list of projects, groups, or all? (Enter 'projects', 'groups', or 'all'): "
            )
            .strip()
            .lower()
        )

        if choice == "projects":
            selected_projects = input(
                "Enter the projects you want to clone, separated by commas: "
            ).split(",")
            cloner.clone_selected_repositories(selected_projects)
        elif choice == "groups":
            selected_groups = input(
                "Enter the groups you want to clone, separated by commas: "
            ).split(",")
            cloner.clone_selected_groups(selected_groups)
        elif choice == "all":
            cloner.clone_all()
        else:
            print("Invalid choice. Please enter 'projects', 'groups', or 'all'.")
