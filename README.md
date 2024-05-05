# GitCloner

This repository contains the `gitlab-clone-repos.py` file, which is a Python script for cloning GitLab repositories.

## Prerequisites

Before running the script, make sure you have the following:

- Python 3.x installed
- Git installed

## Usage

To use the `gitlab-clone-repos.py` script, follow these steps:

1. Clone this repository to your local machine.
2. Open a terminal or command prompt.
3. Navigate to the cloned repository directory.
4. Update the following variables in the script:
    - `GITLAB_URL`: Set your GitLab instance URL.
    - `GITLAB_FQDN`: Set your GitLab fully qualified domain name.
    - `USER_NAME`: Set your GitLab username.
    - `PRIVATE_TOKEN`: Set your GitLab private token.
5. Run the script using the following command:

     ```bash
     python gitlab-clone-repos.py
     ```

     This will clone all the GitLab repositories listed in the script.

## License

This project is licensed under the [GNU V3 License](LICENSE).
