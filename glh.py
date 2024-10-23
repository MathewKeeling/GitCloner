"""
Copyright Notice:

Author: Mathew Keeling
Date: 22 October 2024

Description: Gitlab Helper 2024.10.1

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


class gitlab_helper:
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
            filename="gitlab_helper.log",
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
                        f'cd {project} && git commit -m "gitlab_helper: {current_datetime}"'
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

def create_config_file(config_path):
    config = configparser.ConfigParser()
    config["DEFAULT"] = {
        "selected_url": "gitlab.example.com"
    }
    config["gitlab.example.com"] = {
        "url": "https://gitlab.example.com",
        "user": "your-username",
        "private_token": "your-private-token",
    }
    os.makedirs(os.path.dirname(config_path), exist_ok=True)
    with open(config_path, "w") as configfile:
        config.write(configfile)
    print(f"\nConfiguration file '{config_path}' created with generic values.")
    print("Please update it with your GitLab URL, username, and private token for each hostname.")
    print("Exiting...\n")

def add_config_section(config_path, fqdn):
    config = configparser.ConfigParser()
    config.read(config_path)
    if fqdn not in config:
        config[fqdn] = {
            "url": f"https://{fqdn}",
            "user": "your-username",
            "private_token": "your-private-token",
        }
        with open(config_path, "w") as configfile:
            config.write(configfile)
        print(f"\nConfiguration section '{fqdn}' added to '{config_path}'.")
        print("Please update it with your GitLab URL, username, and private token.\n")
    else:
        print(f"\nConfiguration section '{fqdn}' already exists in '{config_path}'.\n")

def set_selected_url(config_path, fqdn):
    config = configparser.ConfigParser()
    config.read(config_path)
    if fqdn in config:
        config["DEFAULT"]["selected_url"] = fqdn
        with open(config_path, "w") as configfile:
            config.write(configfile)
        print(f"\nSelected URL set to '{fqdn}' in '{config_path}'.\n")
    else:
        print(f"\nError: Configuration section '{fqdn}' does not exist in '{config_path}'.\n")
        exit(1)

def list_urls(config_path):
    config = configparser.ConfigParser()
    config.read(config_path)
    print("\nAvailable URLs:")
    for section in config.sections():
        print(f"- {section}")
    print()

def list_urls(config_path):
    config = configparser.ConfigParser()
    config.read(config_path)
    print("Available URLs:")
    for section in config.sections():
        print(f"- {section}")


if __name__ == "__main__":
    if os.name == 'nt':  # Windows
        config_path = os.path.expanduser("~\\.glh\\glh.ini")
    else:  # Linux and other Unix-like systems
        config_path = os.path.expanduser("~/.glh/glh.ini")

    if not os.path.exists(config_path):
        create_config_file(config_path)
        exit(1)

    parser = argparse.ArgumentParser(
        description="Clone and update GitLab repositories."
    )
    parser.add_argument(
        "--add_url", type=str, help="Fully qualified domain name to add a new configuration section."
    )
    parser.add_argument(
        "--set_url", type=str, help="Set the selected GitLab URL."
    )
    parser.add_argument(
        "--list_url", action="store_true", help="List all available URLs."
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

    if args.add_url:
        add_config_section(config_path, args.add_url)
        exit(0)

    if args.set_url:
        set_selected_url(config_path, args.set_url)
        exit(0)

    if args.list_url:
        list_urls(config_path)
        exit(0)

    config = configparser.ConfigParser()
    config.read(config_path)

    # Determine the selected URL from the config file
    selected_url = config["DEFAULT"]["selected_url"]

    if selected_url not in config:
        print(f"\nNo configuration found for selected URL '{selected_url}'.\n")
        exit(1)

    GITLAB_URL = config[selected_url]["url"]
    USER = config[selected_url]["user"]
    PRIVATE_TOKEN = config[selected_url]["private_token"]

    cloner = gitlab_helper(GITLAB_URL, USER, PRIVATE_TOKEN, verbose=args.verbose)

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
            print("\nInvalid choice. Please enter 'projects', 'groups', or 'all'.\n")